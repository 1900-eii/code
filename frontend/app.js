const projectTitle = document.querySelector("#project-title");
const projectSubtitle = document.querySelector("#project-subtitle");
const heroStats = document.querySelector("#hero-stats");
const taxonomyPills = document.querySelector("#taxonomy-pills");
const workflowGrid = document.querySelector("#workflow-grid");
const datasetGrid = document.querySelector("#dataset-grid");
const plotGrid = document.querySelector("#plot-grid");
const deliverableGrid = document.querySelector("#deliverable-grid");

const stage = document.querySelector("#stage");
const inspector = document.querySelector("#inspector");
const taxonomyFilter = document.querySelector("#taxonomy-filter");
const sortMode = document.querySelector("#sort-mode");
const downloadSceneButton = document.querySelector("#download-scene");
const downloadBlenderFullButton = document.querySelector("#download-blender-full");
const downloadBlenderFullCsvButton = document.querySelector("#download-blender-full-csv");
const downloadBlenderFilteredButton = document.querySelector("#download-blender-filtered");
const downloadBlenderFilteredCsvButton = document.querySelector("#download-blender-filtered-csv");
const downloadBlenderSelectedButton = document.querySelector("#download-blender-selected");

let dashboard = null;
let scene = null;
let blenderPackage = null;
let blenderCsv = "";
let activeId = null;

const readJson = async (path) => {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Failed to load ${path}: ${response.status}`);
  return response.json();
};

const readText = async (path) => {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Failed to load ${path}: ${response.status}`);
  return response.text();
};

const createStat = (label, value) => {
  const pill = document.createElement("div");
  pill.className = "stat";
  pill.innerHTML = `<strong>${value}</strong><span>${label}</span>`;
  return pill;
};

const relativeAssetPath = (path) => `../${path}`;

const toCsv = (rows) => {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  const escape = (value) => {
    const text = String(value ?? "");
    if (text.includes(",") || text.includes("\"") || text.includes("\n")) {
      return `"${text.replace(/"/g, "\"\"")}"`;
    }
    return text;
  };
  return [headers.join(","), ...rows.map((row) => headers.map((key) => escape(row[key])).join(","))].join("\n");
};

const downloadPayload = (payload, filename, mime = "application/json") => {
  const content = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

const svgFragment = (fragment) => {
  const { width, height, depth } = fragment.size;
  const [base, accent, light] = fragment.palette;
  const x = 42;
  const y = 30 + fragment.elevation * 0.35;
  const skew = depth * 0.52;
  const radius = Math.min(18, fragment.radius);

  return `
    <svg class="fragment-svg" width="180" height="150" viewBox="0 0 180 150" aria-hidden="true">
      <defs>
        <linearGradient id="${fragment.id}-front" x1="0" x2="1">
          <stop offset="0%" stop-color="${accent}" />
          <stop offset="100%" stop-color="${light}" />
        </linearGradient>
        <linearGradient id="${fragment.id}-side" x1="0" x2="1">
          <stop offset="0%" stop-color="${base}" />
          <stop offset="100%" stop-color="${accent}" />
        </linearGradient>
      </defs>
      <g transform="rotate(${fragment.tilt} 90 72)">
        <polygon points="${x},${y} ${x + width * 0.46},${y} ${x + width * 0.46 + skew},${y - depth * 0.32} ${x + skew},${y - depth * 0.32}"
          fill="${light}" opacity="0.82" />
        <rect x="${x}" y="${y}" width="${width * 0.46}" height="${height * 0.42}" rx="${radius}" fill="url(#${fragment.id}-front)" />
        <polygon points="${x + width * 0.46},${y} ${x + width * 0.46 + skew},${y - depth * 0.32} ${x + width * 0.46 + skew},${y + height * 0.42 - depth * 0.32} ${x + width * 0.46},${y + height * 0.42}"
          fill="url(#${fragment.id}-side)" opacity="0.95" />
      </g>
    </svg>
  `;
};

const renderHero = () => {
  projectTitle.textContent = dashboard.project.title;
  projectSubtitle.textContent = dashboard.project.subtitle;
  heroStats.innerHTML = "";
  heroStats.append(
    createStat("ML Records", dashboard.highlights.ml_records),
    createStat("Scraped Datasets", dashboard.highlights.scraped_datasets),
    createStat("Structured Rows", dashboard.highlights.structured_rows),
    createStat("Fragments", dashboard.highlights.fragment_count),
    createStat("Status", dashboard.project.status),
  );
};

const renderTaxonomyPills = () => {
  taxonomyPills.innerHTML = "";
  const paletteByTaxonomy = Object.fromEntries(scene.fragments.map((fragment) => [fragment.taxonomy, fragment.palette]));
  Object.entries(dashboard.taxonomy_counts).forEach(([taxonomy, count]) => {
    const palette = paletteByTaxonomy[taxonomy] || ["#1f5c7a", "#ef6c57"];
    const pill = document.createElement("div");
    pill.className = "taxonomy-pill";
    pill.style.background = `linear-gradient(135deg, ${palette[0]}, ${palette[1]})`;
    pill.innerHTML = `<strong>${taxonomy}</strong><span>${count} interaction records</span>`;
    taxonomyPills.appendChild(pill);
  });
};

const renderWorkflow = () => {
  workflowGrid.innerHTML = "";
  dashboard.architecture_steps.forEach((step) => {
    const card = document.createElement("article");
    card.className = "workflow-card";
    card.innerHTML = `
      <div class="workflow-stage">${step.stage}</div>
      <h3>${step.title}</h3>
      <p>${step.body}</p>
    `;
    workflowGrid.appendChild(card);
  });
};

const renderDatasets = () => {
  datasetGrid.innerHTML = "";
  dashboard.datasets.forEach((dataset) => {
    const card = document.createElement("article");
    card.className = "dataset-card";
    const terms = dataset.top_terms.length
      ? dataset.top_terms.map((term) => `<span class="mini-pill">${term}</span>`).join("")
      : `<span class="mini-pill">No extracted keywords</span>`;
    card.innerHTML = `
      <div class="dataset-meta">
        <span class="dataset-type">${dataset.dataset_type}</span>
        <span class="dataset-source">${dataset.source_site}</span>
      </div>
      <h3>${dataset.title}</h3>
      <p>${dataset.summary_text}</p>
      <div class="dataset-stats">
        <div><strong>${dataset.row_count}</strong><span>rows</span></div>
        <div><strong>${dataset.paragraph_count}</strong><span>text chunks</span></div>
      </div>
      <div class="mini-pill-row">${terms}</div>
    `;
    datasetGrid.appendChild(card);
  });
};

const renderPlots = () => {
  plotGrid.innerHTML = "";
  dashboard.plot_cards.forEach((plot) => {
    const card = document.createElement("article");
    card.className = "plot-card";
    card.innerHTML = `
      <img src="${relativeAssetPath(plot.path)}" alt="${plot.title}" />
      <div class="plot-copy">
        <h3>${plot.title}</h3>
        <p>${plot.description}</p>
      </div>
    `;
    plotGrid.appendChild(card);
  });
};

const renderDeliverables = () => {
  deliverableGrid.innerHTML = "";
  dashboard.deliverables.forEach((item) => {
    const parts = item.path.split("/");
    const filename = parts.pop() || item.path;
    const directory = parts.join("/");
    const card = document.createElement("a");
    card.className = "deliverable-card";
    card.href = relativeAssetPath(item.path);
    card.target = "_blank";
    card.rel = "noreferrer";
    card.innerHTML = `
      <strong>${item.label}</strong>
      <span class="deliverable-file">${filename}</span>
      <code class="deliverable-path">${directory}</code>
    `;
    deliverableGrid.appendChild(card);
  });
};

const sortFragments = (fragments) => {
  const mode = sortMode.value;
  const sorted = [...fragments];
  if (mode === "brightness") sorted.sort((a, b) => b.brightness - a.brightness);
  else if (mode === "coverage") sorted.sort((a, b) => b.alpha_coverage_ratio - a.alpha_coverage_ratio);
  else sorted.sort((a, b) => a.timestamp_sec - b.timestamp_sec);
  return sorted;
};

const filteredFragments = () => {
  const selected = taxonomyFilter.value;
  const fragments = selected === "all" ? scene.fragments : scene.fragments.filter((item) => item.taxonomy === selected);
  return sortFragments(fragments);
};

const getBlenderFragmentById = (id) => blenderPackage.fragments.find((item) => item.id === id);

const updateInspector = (fragment) => {
  inspector.innerHTML = `
    <h2>${fragment.title}</h2>
    <div class="inspector-grid">
      <div class="rule-list">
        <div class="rule-item"><strong>Geometry</strong>${fragment.rules.geometry}</div>
        <div class="rule-item"><strong>Material</strong>${fragment.rules.material}</div>
        <div class="rule-item"><strong>Interaction</strong>${fragment.rules.interaction}</div>
        <div class="rule-item"><strong>Color</strong>${fragment.rules.color}</div>
      </div>
      <div class="metric-list">
        <div class="metric-item"><strong>Taxonomy</strong>${fragment.taxonomy}</div>
        <div class="metric-item"><strong>Family</strong>${fragment.family}</div>
        <div class="metric-item"><strong>Timeline</strong>${fragment.timestamp_sec.toFixed(1)} sec</div>
        <div class="metric-item"><strong>Size</strong>${fragment.size.width} × ${fragment.size.height} × ${fragment.size.depth}</div>
        <div class="metric-item"><strong>Coverage / Brightness</strong>${fragment.alpha_coverage_ratio.toFixed(3)} / ${fragment.brightness.toFixed(1)}</div>
        <div class="metric-item"><strong>Keyframe</strong>${fragment.nearest_keyframe}</div>
      </div>
    </div>
    <div class="inspector-preview"><img src="${relativeAssetPath(fragment.source_image)}" alt="${fragment.title}" /></div>
  `;
};

const renderStage = () => {
  const fragments = filteredFragments();
  stage.innerHTML = "";
  if (!fragments.length) {
    stage.textContent = "No fragments match the current filter.";
    return;
  }

  if (!activeId || !fragments.some((item) => item.id === activeId)) activeId = fragments[0].id;

  fragments.forEach((fragment) => {
    const card = document.createElement("article");
    card.className = "fragment-card";
    if (fragment.id === activeId) card.classList.add("is-active");
    card.innerHTML = `
      <div class="fragment-swatch" style="background: linear-gradient(90deg, ${fragment.palette.join(", ")});"></div>
      <div class="fragment-meta">
        <div>
          <h3 class="fragment-title">${fragment.title}</h3>
          <p class="fragment-family">${fragment.family}</p>
        </div>
        <div class="fragment-badge">${fragment.taxonomy}</div>
      </div>
      <div class="fragment-preview">${svgFragment(fragment)}</div>
      <div class="fragment-stats">
        <div><span>Timeline</span>${fragment.timestamp_sec.toFixed(1)}s</div>
        <div><span>Coverage</span>${fragment.alpha_coverage_ratio.toFixed(3)}</div>
        <div><span>Brightness</span>${fragment.brightness.toFixed(1)}</div>
        <div><span>Size</span>${fragment.size.width}×${fragment.size.height}</div>
      </div>
    `;
    card.addEventListener("click", () => {
      activeId = fragment.id;
      renderStage();
    });
    stage.appendChild(card);
  });

  updateInspector(fragments.find((item) => item.id === activeId));
};

const initFilters = () => {
  const taxonomies = [...new Set(scene.fragments.map((item) => item.taxonomy))];
  taxonomies.forEach((taxonomy) => {
    const option = document.createElement("option");
    option.value = taxonomy;
    option.textContent = taxonomy;
    taxonomyFilter.appendChild(option);
  });
  taxonomyFilter.addEventListener("change", renderStage);
  sortMode.addEventListener("change", renderStage);
};

const initDownload = () => {
  downloadSceneButton.addEventListener("click", () => downloadPayload(scene, "scene.json"));
  downloadBlenderFullButton.addEventListener("click", () => downloadPayload(blenderPackage, "blender_ready_fragments_full.json"));
  downloadBlenderFullCsvButton.addEventListener("click", () => downloadPayload(blenderCsv, "blender_ready_fragments_full.csv", "text/csv;charset=utf-8"));

  downloadBlenderFilteredButton.addEventListener("click", () => {
    const visibleIds = filteredFragments().map((item) => item.id);
    const filtered = {
      ...blenderPackage,
      export_scope: "filtered",
      fragment_count: visibleIds.length,
      fragments: blenderPackage.fragments.filter((item) => visibleIds.includes(item.id)),
    };
    downloadPayload(filtered, "blender_ready_fragments_filtered.json");
  });

  downloadBlenderFilteredCsvButton.addEventListener("click", () => {
    const visibleIds = filteredFragments().map((item) => item.id);
    const rows = blenderPackage.fragments
      .filter((item) => visibleIds.includes(item.id))
      .map((item) => ({
        id: item.id,
        name: item.name,
        taxonomy: item.taxonomy,
        family: item.family,
        object_type: item.object_type,
        primitive: item.geometry_params?.primitive ?? "",
        width_m: item.dimensions_m.width,
        depth_m: item.dimensions_m.depth,
        height_m: item.dimensions_m.height,
        loc_x: item.transform.location[0],
        loc_y: item.transform.location[1],
        loc_z: item.transform.location[2],
        rot_z_rad: item.transform.rotation_euler[2],
        brightness: item.visual.brightness,
        alpha_coverage_ratio: item.visual.alpha_coverage_ratio,
        analysis_image: item.source_refs.analysis_image,
      }));
    downloadPayload(toCsv(rows), "blender_ready_fragments_filtered.csv", "text/csv;charset=utf-8");
  });

  downloadBlenderSelectedButton.addEventListener("click", () => {
    const selected = getBlenderFragmentById(activeId);
    if (!selected) return;
    downloadPayload(
      { ...blenderPackage, export_scope: "selected", fragment_count: 1, fragments: [selected] },
      `${selected.id}_blender_fragment.json`,
    );
  });
};

const init = async () => {
  [dashboard, scene, blenderPackage, blenderCsv] = await Promise.all([
    readJson("./data/dashboard.json"),
    readJson("./data/scene.json"),
    readJson("../data/processed/blender_ready_fragments.json"),
    readText("../data/processed/blender_ready_fragments.csv"),
  ]);

  renderHero();
  renderTaxonomyPills();
  renderWorkflow();
  renderDatasets();
  renderPlots();
  renderDeliverables();
  initFilters();
  initDownload();
  renderStage();
};

init().catch((error) => {
  document.body.innerHTML = `<main class="page"><section class="section-card"><h2>Dashboard failed to load</h2><p>${error.message}</p></section></main>`;
});
