from __future__ import annotations

import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = PROJECT_ROOT / "blender" / "blender_ready_fragments.json"
COLLECTION_NAME = "ChildSpaceFragments"


def ensure_collection(name: str):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def clear_collection(collection) -> None:
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name: str, rgba: list[float]):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.48
    return material


def link_object_to_collection(obj, collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def apply_common_metadata(obj, fragment: dict) -> None:
    obj["fragment_id"] = fragment["id"]
    obj["taxonomy"] = fragment["taxonomy"]
    obj["family"] = fragment["family"]
    obj["analysis_image"] = fragment["source_refs"]["analysis_image"]
    obj["timestamp_sec"] = fragment["source_refs"]["timestamp_sec"]
    obj["geometry_rule"] = fragment["rules"]["geometry"]


def create_ribbed_wall(fragment: dict):
    dimensions = fragment["dimensions_m"]
    transform = fragment["transform"]
    params = fragment["geometry_params"]
    bpy.ops.mesh.primitive_cube_add(location=transform["location"], rotation=transform["rotation_euler"])
    parent = bpy.context.active_object
    parent.name = fragment["name"]
    parent.scale = (0.01, 0.01, 0.01)

    count = params["panel_count"]
    spacing = params["panel_spacing_m"]
    thickness = params["panel_thickness_m"]
    width = dimensions["width"]
    depth = dimensions["depth"]
    height = dimensions["height"]

    for idx in range(count):
        x = -width / 2 + spacing * (idx + 0.5)
        offset = (idx % 3) * thickness * 0.45
        bpy.ops.mesh.primitive_cube_add(location=(x, offset, 0))
        rib = bpy.context.active_object
        rib.scale = (max(spacing * 0.35, 0.04), max(thickness, 0.03), max(height / 2, 0.08))
        rib.parent = parent

    return parent


def create_marker_field(fragment: dict):
    dimensions = fragment["dimensions_m"]
    transform = fragment["transform"]
    params = fragment["geometry_params"]
    bpy.ops.mesh.primitive_plane_add(location=transform["location"], rotation=transform["rotation_euler"])
    parent = bpy.context.active_object
    parent.name = fragment["name"]
    parent.scale = (dimensions["width"] / 2, dimensions["depth"] / 2, 1)

    count = params["marker_count"]
    cols = max(2, round(count ** 0.5))
    rows = max(2, (count + cols - 1) // cols)
    step_x = dimensions["width"] / cols
    step_y = dimensions["depth"] / rows
    radius = params["marker_radius_m"]

    created = 0
    for row in range(rows):
        for col in range(cols):
            if created >= count:
                break
            x = -dimensions["width"] / 2 + step_x * (col + 0.5)
            y = -dimensions["depth"] / 2 + step_y * (row + 0.5)
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=max(0.03, params["surface_thickness_m"] * 1.4), location=(x, y, 0.02))
            marker = bpy.context.active_object
            marker.parent = parent
            created += 1
    return parent


def create_stepped_slope(fragment: dict):
    dimensions = fragment["dimensions_m"]
    transform = fragment["transform"]
    params = fragment["geometry_params"]
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=transform["location"], rotation=transform["rotation_euler"])
    parent = bpy.context.active_object
    parent.name = fragment["name"]

    step_count = params["step_count"]
    step_height = params["step_height_m"]
    step_depth = params["step_depth_m"]
    width = dimensions["width"]
    for idx in range(step_count):
        bpy.ops.mesh.primitive_cube_add(
            location=(
                -width / 2 + step_depth * (idx + 0.5),
                0,
                step_height * (idx + 0.5),
            )
        )
        step = bpy.context.active_object
        step.scale = (
            max(step_depth / 2, 0.06),
            max(dimensions["depth"] / 2, 0.08),
            max(step_height / 2, 0.05),
        )
        step.parent = parent
    return parent


def create_fragment(fragment: dict, collection) -> None:
    transform = fragment["transform"]
    primitive = fragment.get("geometry_params", {}).get("primitive", "generic_block")

    if primitive == "ribbed_wall":
        obj = create_ribbed_wall(fragment)
    elif primitive == "marker_field":
        obj = create_marker_field(fragment)
    elif primitive == "stepped_slope":
        obj = create_stepped_slope(fragment)
    else:
        dimensions = fragment["dimensions_m"]
        bpy.ops.mesh.primitive_cube_add(
            location=transform["location"],
            rotation=transform["rotation_euler"],
        )
        obj = bpy.context.active_object
        obj.name = fragment["name"]
        obj.scale = (
            dimensions["width"] / 2,
            dimensions["depth"] / 2,
            dimensions["height"] / 2,
        )

    if obj.type == "MESH":
        modifier = obj.modifiers.new(name="Bevel", type="BEVEL")
        modifier.width = max(0.02, transform["bevel_radius"])
        modifier.segments = 4

    material = make_material(f"{fragment['taxonomy']}_mat", fragment["visual"]["palette_rgba"][0])
    if obj.type == "MESH":
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    else:
        for child in obj.children:
            if child.type == "MESH":
                if child.data.materials:
                    child.data.materials[0] = material
                else:
                    child.data.materials.append(material)

    apply_common_metadata(obj, fragment)
    link_object_to_collection(obj, collection)


def import_fragments(json_path: Path = JSON_PATH) -> None:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    collection = ensure_collection(COLLECTION_NAME)
    clear_collection(collection)
    for fragment in payload["fragments"]:
        create_fragment(fragment, collection)
    print(f"Imported {payload['fragment_count']} fragments from {json_path}")


if __name__ == "__main__":
    import_fragments()
