# 	Child-Space Interaction Workflow

# 儿童与建筑空间互动分析工作流

## Overview | 项目概述

### English

This repository implements a data-driven design workflow centered on one topic:
**analyzing how children interact with architectural or spatial elements in a video, then translating that evidence into reusable design fragments**.

The original repository (in workshop 2) already contained the core machine-learning prototype:

- video sampling
- CLIP-based scene filtering
- YOLO-based open-vocabulary detection
- SAM-based segmentation
- taxonomy assignment for interaction-related space types

This repository has now been extended into a more complete workflow that also includes:

- web scraping from public references
- a second vectorisation route for comparison
- structured tabular outputs for analysis
- visualisation and plotting
- a mock API layer as a substitute for deferred OpenAI integration
- a front-end rendering prototype as a substitute for deferred Blender integration

The result is a system that is no longer just a detection script, but a multi-stage research and design pipeline that can be extended into a real generative or 3D design environment.

### 中文

这个仓库实现的是一套以“**儿童如何与建筑/空间元素发生互动**”为主题的 data-driven design workflow。
核心目标是：**先从视频中识别并提取互动证据，再把这些证据转译成可复用的设计片段与分析结果。**

原始仓库已经包含了最核心的机器学习原型：

- 视频采样
- 基于 CLIP 的场景过滤
- 基于 YOLO 的开放词汇检测
- 基于 SAM 的精细分割
- 面向互动空间类型的 taxonomy 分类

在此基础上，这个仓库已经被补全为一条更完整的工作流，还包括：

- 公共网页数据采集
- 第二种向量化路径与对比
- 面向分析的结构化表格输出
- 可视化与绘图
- 用 mock API 替代暂缓接入的 OpenAI API
- 用前端渲染原型替代暂缓接入的 Blender

因此，这个项目现在不再只是一个识别脚本，而是一个多阶段的研究与设计流程，可以扩展为真正的生成式或3D设计环境。

---

## Project Goal | 项目目标

### English

The system is designed to answer a research-and-design question:

> How can observed child-space interactions be extracted from video evidence, compared with public reference datasets, summarized as analyzable features, and finally translated into architectural fragment logic?

This workflow connects four layers:

1. Observation
   Video-based interaction evidence extracted from real scenes.
2. Reference
   Public web datasets related to playgrounds, urban play, and spatial accessibility.
3. Analysis
   Vectorisation, comparison, plotting, and statistical summarization.
4. Translation
   Design-rule synthesis and fragment rendering for downstream design use.

### 中文

整套系统要回答的是一个“研究 + 设计”问题：

> 如何从真实视频中提取儿童与空间互动的证据，并将其与公共参考数据对照、转成可分析特征，最终再转译为空间片段与设计逻辑？

这条工作流连接了四个层级：

1. 观察层
   从真实场景视频中提取互动证据。
2. 参考层
   采集与 playground、urban play、空间可达性相关的公共网页数据。
3. 分析层
   做向量化、比较、统计和可视化。
4. 转译层
   生成设计规则，并渲染为后续设计可用的 fragment 原型。

---

## System Architecture | 系统架构

### English

The current architecture is organized as a staged pipeline:

```text
Input Video
  -> Existing ML Core (CLIP + YOLO + SAM)
  -> Exported Image Evidence
  -> Structured ML Dataset
  -> Vectorisation + Plotting
  -> Mock Design Rule Layer
  -> Front-End Fragment Renderer
```

At the same time, a second branch runs in parallel:

```text
Public Web Sources
  -> Scraping
  -> Cleaned Text Dataset
  -> CountVectorizer / TF-IDF
  -> Similarity + Projection + Top Terms
```

The two branches are then merged:

- ML evidence contributes spatial observations.
- Scraped reference data contributes contextual and comparative knowledge.
- The mock API converts both into design-rule language.
- The front-end renderer turns those rules into fragment prototypes.

### 中文

当前系统的架构是一条分阶段流水线：

```text
输入视频
  -> 原有 ML 核心（CLIP + YOLO + SAM）
  -> 导出的互动图像证据
  -> 结构化 ML 数据表
  -> 向量化 + 可视化
  -> Mock 设计规则层
  -> 前端 Fragment 渲染器
```

同时还有一条并行支路：

```text
公共网页数据源
  -> 抓取
  -> 清洗后的文本数据集
  -> CountVectorizer / TF-IDF
  -> 相似度 + 投影 + 关键词
```

这两条支路最终汇合：

- ML 结果提供空间观察证据。
- 抓取数据提供参考语境和比较维度。
- mock API 把两者转成设计规则语言。
- 前端渲染器再把规则转成 fragment 原型。

---

## Directory Structure | 目录结构

### English

```text
workshop2/
├── code/
│   ├── index.py
│   ├── mine.py
│   ├── mine-old.py
│   ├── index.ipynb
│   └── mine.ipynb
├── workflow/
│   ├── common.py
│   ├── scrape_datasets.py
│   ├── build_analysis_dataset.py
│   ├── vectorize_and_plot.py
│   ├── blender_placeholder.py
│   ├── mock_api.py
│   ├── export_frontend_scene.py
│   ├── export_blender_package.py
│   ├── generate_submission_notes.py
│   └── run_workflow.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── data/
│       └── scene.json
├── blender/
│   ├── README.md
│   ├── blender_ready_fragments.json
│   ├── blender_ready_fragments.csv
│   └── import_fragments.py
├── data/
│   ├── raw_scraped/
│   ├── processed/
│   └── plots/
├── output/
│   ├── keyframes/
│   ├── final_results/
│   └── video_index.pkl
├── video/
│   └── input.mp4
├── sam_b.pt
├── yolov8x-worldv2.pt
├── requirements.txt
├── README.md
└── SUBMISSION_NOTES.md
```

### 中文

```text
workshop2/
├── code/                       原始 ML 原型脚本与 notebook
│   ├── index.py                关键帧抽样与 CLIP 索引
│   ├── mine.py                 主互动检测流程
│   ├── mine-old.py             旧版检测流程
│   ├── index.ipynb
│   └── mine.ipynb
├── workflow/                   新增的完整工作流脚本
│   ├── common.py               全局路径、常量、通用函数
│   ├── scrape_datasets.py      网页抓取
│   ├── build_analysis_dataset.py  结构化 ML 数据集构建
│   ├── vectorize_and_plot.py   向量化与绘图
│   ├── blender_placeholder.py  Blender 占位种子表导出
│   ├── mock_api.py             Mock API 规则生成
│   ├── export_frontend_scene.py 前端渲染数据导出
│   ├── export_blender_package.py Blender 数据包导出
│   ├── generate_submission_notes.py 自动生成提交说明
│   └── run_workflow.py         串联整条流水线
├── frontend/                   前端 fragment 原型
│   ├── index.html              页面入口
│   ├── styles.css              样式
│   ├── app.js                  交互与渲染逻辑
│   └── data/
│       └── scene.json          前端场景数据
├── blender/                    Blender 导入与导出资源
│   ├── README.md               Blender 使用说明
│   ├── blender_ready_fragments.json Blender JSON 数据包
│   ├── blender_ready_fragments.csv  Blender CSV 摘要
│   └── import_fragments.py     Blender 导入脚本
├── data/
│   ├── raw_scraped/            原始网页 HTML
│   ├── processed/              清洗后的表格、向量、JSON
│   └── plots/                  绘图结果
├── output/                     原始 ML 产物
│   ├── keyframes/              关键帧图片
│   ├── final_results/          互动识别结果图
│   └── video_index.pkl         CLIP 特征索引
├── video/
│   └── input.mp4               输入视频
├── sam_b.pt                    SAM 权重
├── yolov8x-worldv2.pt          YOLO 权重
├── requirements.txt            依赖说明
├── README.md                   当前手册
└── SUBMISSION_NOTES.md         自动生成的交付说明
```

---

## Core Modules | 核心模块说明

### 1. Existing ML Core | 原有机器学习核心

#### English

- [code/index.py](code/index.py)
  Samples keyframes from the input video and stores CLIP embeddings in `output/video_index.pkl`.
- [code/mine.py](code/mine.py)
  The main detection script. It:

  - reads video frames
  - filters non-relevant scenes with CLIP
  - detects children and spatial elements with YOLO
  - segments them with SAM
  - assigns taxonomy labels
  - exports four images per interaction candidate

#### 中文

- [code/index.py](code/index.py)
  从输入视频中抽取关键帧，并把 CLIP 特征保存到 `output/video_index.pkl`。
- [code/mine.py](code/mine.py)
  主识别脚本。它会：

  - 读取视频帧
  - 用 CLIP 过滤无关场景
  - 用 YOLO 检测儿童与空间元素
  - 用 SAM 做精细分割
  - 分配 taxonomy 标签
  - 为每个互动候选导出四张分析图

### 2. Workflow Utilities | 新增工作流模块

#### English

- [workflow/common.py](workflow/common.py)
  Shared paths, scrape definitions, regex parsing, and utility helpers.
- [workflow/scrape_datasets.py](workflow/scrape_datasets.py)
  Scrapes public references from:

  - OpenStreetMap playground data for London
  - OpenStreetMap playground data for Camden
  - OpenStreetMap playground data for Islington
  - Spacescape Playscapes article
- [workflow/build_analysis_dataset.py](workflow/build_analysis_dataset.py)
  Converts exported image sets into a structured table and links each record to the nearest CLIP keyframe.
- [workflow/vectorize_and_plot.py](workflow/vectorize_and_plot.py)
  Runs text vectorisation, PCA, similarity analysis, and produces plots.
- [workflow/mock_api.py](workflow/mock_api.py)
  Simulates a downstream generative/analytical API response using deterministic design-rule templates.
- [workflow/export_frontend_scene.py](workflow/export_frontend_scene.py)
  Translates analysis outputs into front-end scene fragments.
- [workflow/export_blender_package.py](workflow/export_blender_package.py)
  Builds a Blender-ready JSON / CSV package from the rendered fragments.
- [workflow/generate_submission_notes.py](workflow/generate_submission_notes.py)
  Builds a concise handoff/report note automatically.
- [workflow/run_workflow.py](workflow/run_workflow.py)
  Runs all stages in sequence.

#### 中文

- [workflow/common.py](workflow/common.py)
  定义共用路径、抓取配置、文件解析规则和基础工具函数。
- [workflow/scrape_datasets.py](workflow/scrape_datasets.py)
  抓取公共参考数据，目前包括：

  - OpenStreetMap 的 London playground 数据
  - OpenStreetMap 的 Camden playground 数据
  - OpenStreetMap 的 Islington playground 数据
  - Spacescape Playscapes 文章
- [workflow/build_analysis_dataset.py](workflow/build_analysis_dataset.py)
  把导出的互动图片结果转成结构化表格，并把每条记录关联到最近的 CLIP 关键帧。
- [workflow/vectorize_and_plot.py](workflow/vectorize_and_plot.py)
  负责文本向量化、PCA、相似度分析和绘图输出。
- [workflow/mock_api.py](workflow/mock_api.py)
  用确定性的设计规则模板模拟后续生成式/分析型 API 的响应。
- [workflow/export_frontend_scene.py](workflow/export_frontend_scene.py)
  把分析结果转成前端场景 fragment 数据。
- [workflow/export_blender_package.py](workflow/export_blender_package.py)
  从渲染 fragments 中生成 Blender 可直接使用的 JSON / CSV 数据包。
- [workflow/generate_submission_notes.py](workflow/generate_submission_notes.py)
  自动生成交付和报告摘要。
- [workflow/run_workflow.py](workflow/run_workflow.py)
  负责顺序执行全部模块。

### 3. Front-End Renderer | 前端渲染器

#### English

The front-end is a browser-based substitute for the deferred Blender stage.

- [frontend/index.html](frontend/index.html)
  Page skeleton and controls.
- [frontend/styles.css](frontend/styles.css)
  Visual system and layout.
- [frontend/app.js](frontend/app.js)
  Loads `scene.json`, filters fragments, renders cards, and shows an inspector panel.
- [frontend/data/scene.json](frontend/data/scene.json)
  Renderable fragment definitions exported from the workflow.

#### 中文

前端部分是对暂缓 Blender 阶段的一种浏览器替代方案。

- [frontend/index.html](frontend/index.html)
  页面结构与控件入口。
- [frontend/styles.css](frontend/styles.css)
  负责视觉系统和版式。
- [frontend/app.js](frontend/app.js)
  读取 `scene.json`，完成筛选、卡片渲染和 inspector 面板交互。
- [frontend/data/scene.json](frontend/data/scene.json)
  由 workflow 导出的可渲染 fragment 数据。

---

## Technical Stack | 技术栈

### English

#### Existing ML stack

- Python 3.10
- OpenCV
- PyTorch
- CLIP
- Ultralytics YOLO
- SAM
- PIL
- NumPy

#### Added analysis stack

- Pandas
- scikit-learn
- Matplotlib
- Seaborn
- Requests
- BeautifulSoup4

#### Front-end stack

- HTML
- CSS
- Vanilla JavaScript
- static JSON scene data

### 中文

#### 原有 ML 技术栈

- Python 3.10
- OpenCV
- PyTorch
- CLIP
- Ultralytics YOLO
- SAM
- PIL
- NumPy

#### 新增分析技术栈

- Pandas
- scikit-learn
- Matplotlib
- Seaborn
- Requests
- BeautifulSoup4

#### 前端技术栈

- HTML
- CSS
- 原生 JavaScript
- 静态 JSON 场景数据

---

## Data Model | 数据模型

### English

The workflow uses several linked data layers:

- Raw video evidence
- Exported interaction images
- Keyframe CLIP vectors
- Scraped text datasets
- Structured interaction table
- Text vector matrices
- Mock design rules
- Front-end scene fragments

The most important structured file is:

- [data/processed/ml_interactions.csv](data/processed/ml_interactions.csv)

It contains fields such as:

- `record_id`
- `taxonomy_label`
- `frame_idx`
- `timestamp_sec`
- `nearest_keyframe_path`
- `alpha_coverage_ratio`
- `raw_brightness`
- `crop_width`
- `crop_height`
- image output paths

### 中文

整套流程使用了多层互相关联的数据结构：

- 原始视频证据
- 导出的互动图像
- 关键帧 CLIP 向量
- 抓取到的文本数据集
- 结构化互动表
- 文本向量矩阵
- mock 设计规则
- 前端 fragment 场景数据

其中最关键的结构化文件是：

- [data/processed/ml_interactions.csv](data/processed/ml_interactions.csv)

它包含例如以下字段：

- `record_id`
- `taxonomy_label`
- `frame_idx`
- `timestamp_sec`
- `nearest_keyframe_path`
- `alpha_coverage_ratio`
- `raw_brightness`
- `crop_width`
- `crop_height`
- 各类图像输出路径

---

## Workflow Stages | 工作流阶段

### Stage 1. Existing ML Extraction | 阶段 1：原有 ML 互动提取

#### English

The original system generates four images for each accepted interaction:

- cutout image
- source image with boxes
- raw crop
- analysis image

These files are stored in `output/final_results`.

#### 中文

原始系统会为每个通过筛选的互动样本导出四张图：

- 抠图
- 带框原图
- 原始裁剪
- 分析图

这些文件保存在 `output/final_results`。

### Stage 2. Scraping Public References | 阶段 2：抓取公共参考数据

#### English

The scraper collects three datasets from two websites and stores:

- raw HTML in `data/raw_scraped`
- cleaned tables in `data/processed`

This satisfies the coursework requirement for multi-source web scraping.

#### 中文

抓取模块会从两个网站采集三个数据集，并分别保存：

- 原始 HTML 到 `data/raw_scraped`
- 清洗后的表格到 `data/processed`

这一阶段满足课程关于“多网站网页抓取”的要求。

### Stage 3. Structuring ML Evidence | 阶段 3：结构化 ML 结果

#### English

This stage parses image filenames, reconstructs each result set, computes image-derived metrics, and matches each interaction to its nearest precomputed CLIP keyframe embedding.

#### 中文

这一阶段会解析图片文件名、还原每组互动结果、计算图像统计指标，并把每个互动样本匹配到最近的 CLIP 关键帧特征。

### Stage 4. Vectorisation and Comparison | 阶段 4：向量化与方法对比

#### English

Two vectorisation routes are used:

- CLIP vectors for image-side semantics
- CountVectorizer and TF-IDF for text-side comparison

This satisfies the requirement that vectorisation should not rely on only one method.

#### 中文

当前项目使用了两条向量化路径：

- 图像语义侧使用 CLIP 向量
- 文本比较侧使用 CountVectorizer 与 TF-IDF

这满足了课程“不只使用一种 vectorisation 方法”的要求。

### Stage 5. Visualisation | 阶段 5：可视化

#### English

The workflow generates plots for:

- taxonomy distribution
- interaction timeline
- CLIP PCA projection
- engineered feature PCA projection
- count-vector similarity
- TF-IDF similarity
- TF-IDF dataset projection

#### 中文

当前流程会输出以下图表：

- taxonomy 分布图
- 互动时间轴散点图
- CLIP PCA 投影图
- 工程特征 PCA 投影图
- CountVector 相似度热力图
- TF-IDF 相似度热力图
- TF-IDF 数据集投影图

### Stage 6. Mock API Design Rules | 阶段 6：Mock API 设计规则

#### English

Instead of calling OpenAI for now, the system creates a mock response that simulates what a downstream design-rule generation layer might return.

This produces:

- taxonomy-specific families
- geometry rules
- material rules
- interaction rules
- color rules

#### 中文

当前并未真实调用 OpenAI，而是先生成一份 mock 响应，用来模拟后续设计规则生成层的输出。

它会为不同 taxonomy 生成：

- fragment family
- geometry rule
- material rule
- interaction rule
- color rule

### Stage 7. Front-End Fragment Rendering | 阶段 7：前端 fragment 渲染

#### English

The browser renderer converts the analysis output into renderable fragment cards. Each fragment stores:

- taxonomy
- family
- size
- brightness
- coverage
- palette
- rule set
- source image path

This is a front-end substitute for the deferred Blender stage.

The page also supports:

- exporting the full Blender dataset
- exporting only the current filtered subset
- exporting only the selected fragment

#### 中文

浏览器渲染器会把分析结果转成可视化 fragment 卡片。每个 fragment 包含：

- taxonomy
- family
- 尺寸
- 亮度
- coverage
- 调色板
- 规则集
- 源图路径

这一步是对暂缓 Blender 阶段的前端替代。

同时页面现在还支持：

- 导出完整 Blender 数据集
- 仅导出当前筛选结果
- 仅导出当前选中的 fragment

---

## Key Outputs | 关键输出文件

### English

#### Structured data

- [data/processed/ml_interactions.csv](data/processed/ml_interactions.csv)
- [data/processed/ml_interactions_summary.json](data/processed/ml_interactions_summary.json)
- [data/processed/ml_clip_vectors.npy](data/processed/ml_clip_vectors.npy)
- [data/processed/engineered_vectors.npy](data/processed/engineered_vectors.npy)

#### Scraped data

- [data/processed/scraped_datasets.csv](data/processed/scraped_datasets.csv)
- [data/processed/scraped_paragraphs.csv](data/processed/scraped_paragraphs.csv)
- [data/processed/scraped_datasets_manifest.json](data/processed/scraped_datasets_manifest.json)

#### Vectorisation and comparison

- [data/processed/vector_method_summary.csv](data/processed/vector_method_summary.csv)
- [data/processed/text_top_terms.csv](data/processed/text_top_terms.csv)
- [data/processed/count_similarity.csv](data/processed/count_similarity.csv)
- [data/processed/tfidf_similarity.csv](data/processed/tfidf_similarity.csv)

#### Render and report outputs

- [data/processed/mock_api_design_rules.json](data/processed/mock_api_design_rules.json)
- [data/processed/blender_fragment_seed_table.csv](data/processed/blender_fragment_seed_table.csv)
- [data/processed/blender_ready_fragments.json](data/processed/blender_ready_fragments.json)
- [data/processed/blender_ready_fragments.csv](data/processed/blender_ready_fragments.csv)
- [frontend/data/scene.json](frontend/data/scene.json)
- [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)

#### Plots

- [data/plots/taxonomy_distribution.png](data/plots/taxonomy_distribution.png)
- [data/plots/interaction_timeline.png](data/plots/interaction_timeline.png)
- [data/plots/engineered_pca.png](data/plots/engineered_pca.png)
- [data/plots/clip_pca.png](data/plots/clip_pca.png)
- [data/plots/count_similarity_heatmap.png](data/plots/count_similarity_heatmap.png)
- [data/plots/tfidf_similarity_heatmap.png](data/plots/tfidf_similarity_heatmap.png)
- [data/plots/tfidf_projection.png](data/plots/tfidf_projection.png)

### 中文

#### 结构化数据

- [data/processed/ml_interactions.csv](data/processed/ml_interactions.csv)
- [data/processed/ml_interactions_summary.json](data/processed/ml_interactions_summary.json)
- [data/processed/ml_clip_vectors.npy](data/processed/ml_clip_vectors.npy)
- [data/processed/engineered_vectors.npy](data/processed/engineered_vectors.npy)

#### 抓取数据

- [data/processed/scraped_datasets.csv](data/processed/scraped_datasets.csv)
- [data/processed/scraped_paragraphs.csv](data/processed/scraped_paragraphs.csv)
- [data/processed/scraped_datasets_manifest.json](data/processed/scraped_datasets_manifest.json)

#### 向量化与对比

- [data/processed/vector_method_summary.csv](data/processed/vector_method_summary.csv)
- [data/processed/text_top_terms.csv](data/processed/text_top_terms.csv)
- [data/processed/count_similarity.csv](data/processed/count_similarity.csv)
- [data/processed/tfidf_similarity.csv](data/processed/tfidf_similarity.csv)

#### 渲染与报告输出

- [data/processed/mock_api_design_rules.json](data/processed/mock_api_design_rules.json)
- [data/processed/blender_fragment_seed_table.csv](data/processed/blender_fragment_seed_table.csv)
- [data/processed/blender_ready_fragments.json](data/processed/blender_ready_fragments.json)
- [data/processed/blender_ready_fragments.csv](data/processed/blender_ready_fragments.csv)
- [frontend/data/scene.json](frontend/data/scene.json)
- [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)

#### 图表

- [data/plots/taxonomy_distribution.png](data/plots/taxonomy_distribution.png)
- [data/plots/interaction_timeline.png](data/plots/interaction_timeline.png)
- [data/plots/engineered_pca.png](data/plots/engineered_pca.png)
- [data/plots/clip_pca.png](data/plots/clip_pca.png)
- [data/plots/count_similarity_heatmap.png](data/plots/count_similarity_heatmap.png)
- [data/plots/tfidf_similarity_heatmap.png](data/plots/tfidf_similarity_heatmap.png)
- [data/plots/tfidf_projection.png](data/plots/tfidf_projection.png)

---

## How To Run | 如何运行

### English

#### 1. Install dependencies

```bash
pip install -r requirements.txt
```

#### 2. Run the full workflow

```bash
python -m workflow.run_workflow
```

#### 3. Launch the front-end prototype

```bash
python -m http.server 8000
```

Then open:

- [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)

### 中文

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行完整工作流

```bash
python -m workflow.run_workflow
```

#### 3. 启动前端原型

```bash
python -m http.server 8000
```

然后打开：

- [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)

---

## Current Status | 当前状态

### English

At the time of writing, the workflow has already been run successfully and produced:

- 147 structured ML interaction records
- 4 scraped reference datasets from 2 websites
- multiple plots and similarity outputs
- 3 taxonomy-level mock design-rule families
- 24 front-end-rendered fragments

### 中文

截至当前，这套工作流已经成功跑通，并产出了：

- `147` 条结构化 ML 互动记录
- 来自 `2` 个网站的 `4` 个抓取数据集
- 多张图表和相似度分析结果
- `3` 组 taxonomy 级别的 mock 设计规则
- `24` 个前端渲染的 fragments

---

## Deferred / Substitute Components | 暂缓 / 替代组件

### English

#### OpenAI API

Deferred for now. Substitute:

- [workflow/mock_api.py](workflow/mock_api.py)

This keeps the workflow structurally complete while avoiding API dependency during development.

#### Blender

Partially implemented through an export + import bridge.

- [workflow/blender_placeholder.py](workflow/blender_placeholder.py)
- [workflow/export_frontend_scene.py](workflow/export_frontend_scene.py)
- [workflow/export_blender_package.py](workflow/export_blender_package.py)
- [blender/import_fragments.py](blender/import_fragments.py)
- [frontend](frontend)

This means the project can now export Blender-ready fragment data and import it into Blender through a Python script, even though it still uses simplified geometry rather than a fully bespoke modeling pipeline.

The Blender bridge currently supports:

- full JSON export
- filtered JSON export from the front-end
- selected fragment export from the front-end
- CSV export for review and editing
- taxonomy-aware simplified geometry import inside Blender

### 中文

#### OpenAI API

目前暂缓。替代方案：

- [workflow/mock_api.py](workflow/mock_api.py)

这样可以在开发阶段保持工作流结构完整，同时避免 API 依赖。

#### Blender

现在已经实现了“导出 + 导入”桥接版本。

- [workflow/blender_placeholder.py](workflow/blender_placeholder.py)
- [workflow/export_frontend_scene.py](workflow/export_frontend_scene.py)
- [workflow/export_blender_package.py](workflow/export_blender_package.py)
- [blender/import_fragments.py](blender/import_fragments.py)
- [frontend](frontend)

这意味着当前项目已经可以导出 Blender 可用的 fragment 数据，并通过 Python 脚本导入 Blender；只是当前导入的是简化几何，而不是完全定制化的建模逻辑。

当前 Blender 桥接层支持：

- 完整 JSON 导出
- 前端筛选结果 JSON 导出
- 当前选中 fragment 的单体导出
- CSV 导出，便于人工检查和编辑
- 在 Blender 中按 taxonomy 导入不同的简化几何类型

---

## Limitations | 当前限制

### English

- The current Python environment does not include installed `clip` and `ultralytics`, so the existing ML outputs are reused rather than recomputed.
- The front-end renderer is a design-oriented visualization prototype, not a full geometry engine.
- The web scraping currently prioritizes stable public pages over complex API-based structured downloads.
- The mock API is deterministic and template-based, so it does not provide true generative variation.

### 中文

- 当前 Python 环境未安装 `clip` 和 `ultralytics`，因此系统复用了现有 ML 输出，而没有重新计算。
- 前端渲染器是面向设计展示的原型，不是完整几何引擎。
- 当前网页抓取优先选择稳定的公共页面，而不是更复杂的 API 化结构下载。
- mock API 是模板化、确定性的。

---


## Quick Entry Points | 快速入口

### English

- Full workflow runner:
  [workflow/run_workflow.py](workflow/run_workflow.py)
- Main ML script:
  [code/mine.py](code/mine.py)
- Front-end prototype:
  [frontend/index.html](frontend/index.html)
- Submission summary:
  [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)

### 中文

- 完整 workflow 入口：
  [workflow/run_workflow.py](workflow/run_workflow.py)
- 主 ML 脚本：
  [code/mine.py](code/mine.py)
- 前端原型入口：
  [frontend/index.html](frontend/index.html)
- 提交摘要：
  [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)
