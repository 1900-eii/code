from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from workflow.common import PLOTS_DIR, PROCESSED_DIR, ensure_directories, write_json


sns.set_theme(style="whitegrid")


def save_plot(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_taxonomy_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 4.5))
    order = df["taxonomy_label"].value_counts().index
    sns.countplot(data=df, y="taxonomy_label", hue="taxonomy_label", order=order, palette="crest", legend=False)
    plt.title("Interaction Count by Taxonomy")
    plt.xlabel("Count")
    plt.ylabel("Taxonomy")
    save_plot(PLOTS_DIR / "taxonomy_distribution.png")


def plot_timeline(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 4.5))
    sns.scatterplot(
        data=df,
        x="timestamp_sec",
        y="taxonomy_label",
        hue="alpha_coverage_ratio",
        size="crop_width",
        sizes=(20, 220),
        palette="viridis",
    )
    plt.title("Interaction Timeline Across the Video")
    plt.xlabel("Timestamp (sec)")
    plt.ylabel("Taxonomy")
    save_plot(PLOTS_DIR / "interaction_timeline.png")


def plot_scraped_row_counts(datasets_df: pd.DataFrame) -> None:
    structured = datasets_df[datasets_df["dataset_type"] == "structured_geospatial"].copy()
    if structured.empty:
        return
    plt.figure(figsize=(8.5, 4.5))
    sns.barplot(data=structured, x="dataset_name", y="row_count", hue="dataset_name", palette="flare", legend=False)
    plt.title("Structured Scraped Dataset Row Counts")
    plt.xlabel("Dataset")
    plt.ylabel("Rows")
    plt.xticks(rotation=20, ha="right")
    save_plot(PLOTS_DIR / "scraped_row_counts.png")


def plot_engineered_pca(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "crop_width",
        "crop_height",
        "aspect_ratio",
        "alpha_coverage_ratio",
        "raw_mean_r",
        "raw_mean_g",
        "raw_mean_b",
        "raw_brightness",
        "analysis_std_r",
        "analysis_std_g",
        "analysis_std_b",
    ]
    features = df[numeric_cols].copy()
    taxonomy_one_hot = pd.get_dummies(df["taxonomy_label"], prefix="taxonomy")
    matrix = pd.concat([features, taxonomy_one_hot], axis=1)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    plot_df = df[["record_id", "taxonomy_label"]].copy()
    plot_df["pc1"] = coords[:, 0]
    plot_df["pc2"] = coords[:, 1]

    plt.figure(figsize=(7.5, 6))
    sns.scatterplot(data=plot_df, x="pc1", y="pc2", hue="taxonomy_label", palette="Set2", s=75)
    plt.title("Engineered Interaction Features (PCA)")
    save_plot(PLOTS_DIR / "engineered_pca.png")

    plot_df.to_csv(PROCESSED_DIR / "engineered_feature_projection.csv", index=False)
    np.save(PROCESSED_DIR / "engineered_vectors.npy", scaled.astype(np.float32))
    return pd.DataFrame(
        {
            "method": ["engineered"],
            "vector_dim": [int(scaled.shape[1])],
            "pc1_explained": [float(pca.explained_variance_ratio_[0])],
            "pc2_explained": [float(pca.explained_variance_ratio_[1])],
        }
    )


def plot_clip_pca(df: pd.DataFrame) -> pd.DataFrame:
    clip_vectors = np.load(PROCESSED_DIR / "ml_clip_vectors.npy")
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(clip_vectors)
    plot_df = df[["record_id", "taxonomy_label"]].copy()
    plot_df["pc1"] = coords[:, 0]
    plot_df["pc2"] = coords[:, 1]

    plt.figure(figsize=(7.5, 6))
    sns.scatterplot(data=plot_df, x="pc1", y="pc2", hue="taxonomy_label", palette="Dark2", s=75)
    plt.title("Nearest-Keyframe CLIP Features (PCA)")
    save_plot(PLOTS_DIR / "clip_pca.png")

    plot_df.to_csv(PROCESSED_DIR / "clip_feature_projection.csv", index=False)
    return pd.DataFrame(
        {
            "method": ["clip"],
            "vector_dim": [int(clip_vectors.shape[1])],
            "pc1_explained": [float(pca.explained_variance_ratio_[0])],
            "pc2_explained": [float(pca.explained_variance_ratio_[1])],
        }
    )


def top_terms(frame: pd.DataFrame, prefix: str, vectorizer, matrix) -> pd.DataFrame:
    terms = np.asarray(vectorizer.get_feature_names_out())
    rows = []
    for idx, dataset_name in enumerate(frame["dataset_name"]):
        weights = np.asarray(matrix[idx]).ravel()
        top_idx = np.argsort(weights)[::-1][:10]
        rows.append(
            {
                "dataset_name": dataset_name,
                "method": prefix,
                "top_terms": ", ".join(term for term in terms[top_idx] if weights[np.where(terms == term)[0][0]] > 0),
            }
        )
    return pd.DataFrame(rows)


def vectorize_text(datasets_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    texts = (
        datasets_df["summary_text"].fillna(datasets_df["full_text"])
        .fillna("")
        .where(lambda col: col.str.len() > 0, datasets_df["title"].fillna("") + ". " + datasets_df["topic"].fillna(""))
        .tolist()
    )
    count_vectorizer = CountVectorizer(stop_words="english", max_features=80)
    tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=80, ngram_range=(1, 2))
    count_matrix = count_vectorizer.fit_transform(texts)
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)

    count_similarity = cosine_similarity(count_matrix)
    tfidf_similarity = cosine_similarity(tfidf_matrix)

    sim_labels = datasets_df["dataset_name"].tolist()
    count_df = pd.DataFrame(count_similarity, index=sim_labels, columns=sim_labels)
    tfidf_df = pd.DataFrame(tfidf_similarity, index=sim_labels, columns=sim_labels)
    count_df.to_csv(PROCESSED_DIR / "count_similarity.csv")
    tfidf_df.to_csv(PROCESSED_DIR / "tfidf_similarity.csv")

    plt.figure(figsize=(6, 5))
    sns.heatmap(count_df, annot=True, cmap="Blues", vmin=0, vmax=1)
    plt.title("Count Vector Similarity")
    save_plot(PLOTS_DIR / "count_similarity_heatmap.png")

    plt.figure(figsize=(6, 5))
    sns.heatmap(tfidf_df, annot=True, cmap="magma", vmin=0, vmax=1)
    plt.title("TF-IDF Similarity")
    save_plot(PLOTS_DIR / "tfidf_similarity_heatmap.png")

    tfidf_svd = TruncatedSVD(n_components=2, random_state=42)
    coords = tfidf_svd.fit_transform(tfidf_matrix)
    projection = datasets_df[["dataset_name", "source_site"]].copy()
    projection["x"] = coords[:, 0]
    projection["y"] = coords[:, 1]

    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=projection, x="x", y="y", hue="source_site", style="dataset_name", s=120)
    plt.title("Scraped Dataset TF-IDF Projection")
    save_plot(PLOTS_DIR / "tfidf_projection.png")

    projection.to_csv(PROCESSED_DIR / "scraped_tfidf_projection.csv", index=False)
    top_terms_df = pd.concat(
        [
            top_terms(datasets_df, "count", count_vectorizer, count_matrix.toarray()),
            top_terms(datasets_df, "tfidf", tfidf_vectorizer, tfidf_matrix.toarray()),
        ],
        ignore_index=True,
    )
    top_terms_df.to_csv(PROCESSED_DIR / "text_top_terms.csv", index=False)

    comparison = pd.DataFrame(
        [
            {
                "method": "count_vectorizer",
                "vector_dim": int(count_matrix.shape[1]),
                "notes": "Captures raw term frequency and preserves repeated urban-play keywords.",
            },
            {
                "method": "tfidf",
                "vector_dim": int(tfidf_matrix.shape[1]),
                "notes": "Downweights generic terms and emphasizes site-specific planning vocabulary.",
            },
        ]
    )
    return top_terms_df, comparison


def export_report_inputs(
    df: pd.DataFrame,
    datasets_df: pd.DataFrame,
    top_terms_df: pd.DataFrame,
    vector_summary: pd.DataFrame,
) -> None:
    insights = {
        "ml_summary": {
            "record_count": int(len(df)),
            "taxonomy_counts": df["taxonomy_label"].value_counts().to_dict(),
            "mean_alpha_coverage_ratio": round(float(df["alpha_coverage_ratio"].mean()), 4),
            "brightest_taxonomy": df.groupby("taxonomy_label")["raw_brightness"].mean().idxmax(),
        },
        "text_summary": {
            "dataset_count": int(len(datasets_df)),
            "top_terms_by_method": top_terms_df.to_dict(orient="records"),
        },
        "vector_methods": vector_summary.to_dict(orient="records"),
        "deferred_modules": [
            "OpenAI API integration is scaffolded but not executed.",
            "Blender fragment generation is scaffolded but not executed.",
        ],
    }
    write_json(PROCESSED_DIR / "analysis_report_inputs.json", insights)


def main() -> None:
    ensure_directories()
    ml_df = pd.read_csv(PROCESSED_DIR / "ml_interactions.csv")
    datasets_df = pd.read_csv(PROCESSED_DIR / "scraped_datasets.csv")

    plot_taxonomy_distribution(ml_df)
    plot_timeline(ml_df)
    plot_scraped_row_counts(datasets_df)
    engineered_summary = plot_engineered_pca(ml_df)
    clip_summary = plot_clip_pca(ml_df)
    top_terms_df, text_summary = vectorize_text(datasets_df)

    vector_summary = pd.concat([clip_summary, engineered_summary, text_summary], ignore_index=True)
    vector_summary.to_csv(PROCESSED_DIR / "vector_method_summary.csv", index=False)
    export_report_inputs(ml_df, datasets_df, top_terms_df, vector_summary)
    print(f"Saved plots to {PLOTS_DIR} and vectors to {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
