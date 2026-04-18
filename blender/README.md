# Blender Import Guide

## Files

- `blender_ready_fragments.json`
  Structured fragment package with dimensions, transforms, visual properties, and rule metadata.
- `blender_ready_fragments.csv`
  Flat summary table for manual review or spreadsheet editing.
- `import_fragments.py`
  Blender Python importer.

## Workflow

1. Run the project workflow:

```bash
python -m workflow.run_workflow
```

2. Optionally open the front-end and export:
   - full Blender JSON
   - filtered Blender JSON / CSV
   - selected fragment JSON

3. Open Blender.
4. Switch to the Scripting workspace.
5. Open `blender/import_fragments.py`.
6. Adjust `JSON_PATH` if you exported a custom file.
7. Run the script.

## What the importer creates

- A collection named `ChildSpaceFragments`
- Taxonomy-aware simplified geometry:
  - `edge_condition` -> ribbed wall panels
  - `playable_surface` -> plane with circular markers
  - `sloped_platform` -> stepped slope assembly
- Materials based on taxonomy palette
- Per-object metadata for future scripting

## Notes

- This importer creates a first-pass parametric representation, not final bespoke modeling.
- The exported metadata is designed to be extended into instancing, animation, procedural materials, or more complex geometry later.
