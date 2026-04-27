# Submission Notes

## Project Status

This repository now contains a complete non-OpenAI, non-Blender workflow for the child-space interaction design study.

## Completed Parts

- Web scraping: 4 public datasets from 2 websites
- Dataset vectorisation: CLIP keyframe vectors plus CountVectorizer and TF-IDF comparison
- Visualising / plotting: taxonomy distribution, timeline, PCA plots, and similarity heatmaps
- Machine learning integration: 147 structured interaction records built from the existing YOLO + SAM + CLIP outputs
- API substitute: mock design-rule response that simulates downstream analytical generation
- Software integration substitute: front-end fragment renderer with 24 fragments
- Blender bridge: Blender-ready JSON / CSV package plus Blender Python import script

## Evidence Summary

- ML interaction records: 147
- Taxonomy counts: {'sloped_platform': 69, 'edge_condition': 63, 'playable_surface': 15}
- Scraped datasets: ['london_playgrounds_osm', 'camden_playgrounds_osm', 'islington_playgrounds_osm', 'playscapes_global_map']
- Vector methods: ['clip', 'engineered', 'count_vectorizer', 'tfidf']
- Fragment count in front-end scene: 24

## Mock API Design Families

### edge_condition

- Family: threshold wall
- Geometry rule: repeat narrow vertical ribs and offset every third panel
- Material rule: use perforated metal or translucent acrylic panels
- Interaction rule: keep apertures at child-eye level and alternate dense/open zones
- Color rule: lean toward saturated warning tones with one bright accent

### playable_surface

- Family: ground field
- Geometry rule: tile the surface with rhythmic circular or hopscotch-like markers
- Material rule: use painted rubber, terrazzo, or textured paving
- Interaction rule: encode movement prompts as directional traces and soft landing pockets
- Color rule: use high-contrast stripes and warm ground colors

### sloped_platform

- Family: inhabitable slope
- Geometry rule: stack broad terraces and taper every second edge to create climbable transitions
- Material rule: use timber slats, coated plywood, or soft composite seating surfaces
- Interaction rule: balance sitting, climbing, and pause zones across the slope
- Color rule: keep the base warm and highlight slope transitions with brighter bands
