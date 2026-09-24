"""Create the redistributable native scene used in documentation captures."""

from __future__ import annotations

import os
from pathlib import Path

import bpy
from mathutils import Vector


repository = Path(__file__).resolve().parents[1]
project = repository / "test-output" / "Portfolio"
sources = project / "sources"
sources.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.75), scale=(1.5, 1.0, 0.75))
crate = bpy.context.active_object
crate.name = "WorkshopCrate"
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
if not crate.data.uv_layers:
    crate.data.uv_layers.new(name="UVMap")

material = bpy.data.materials.new(name="WorkshopPaint")
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0.055, 0.18, 0.32, 1.0)
principled.inputs["Metallic"].default_value = 0.35
principled.inputs["Roughness"].default_value = 0.28
crate.data.materials.append(material)

bevel = crate.modifiers.new(name="PresentationBevel", type="BEVEL")
bevel.width = 0.08
bevel.segments = 4

bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.active_object
ground.name = "PresentationGround"
ground_material = bpy.data.materials.new(name="GroundMaterial")
ground_principled = ground_material.node_tree.nodes.get("Principled BSDF")
ground_principled.inputs["Base Color"].default_value = (0.025, 0.03, 0.045, 1.0)
ground_principled.inputs["Roughness"].default_value = 0.7
ground.data.materials.append(ground_material)

bpy.ops.object.light_add(type="AREA", location=(4.0, -3.0, 6.0))
key_light = bpy.context.active_object
key_light.name = "PresentationKey"
key_light.data.energy = 950.0
key_light.data.shape = "DISK"
key_light.data.size = 4.0

bpy.ops.object.light_add(type="AREA", location=(-4.0, 1.0, 3.0))
fill_light = bpy.context.active_object
fill_light.name = "PresentationFill"
fill_light.data.energy = 500.0
fill_light.data.color = (0.22, 0.45, 1.0)
fill_light.data.size = 3.0

bpy.ops.object.camera_add(location=(5.5, -7.0, 4.4))
camera = bpy.context.active_object
camera.name = "PresentationCamera"
direction = Vector((0.0, 0.0, 0.8)) - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
# Normal example/acceptance runs must never dirty a tracked documentation
# artifact. Updating the checked-in image is an explicit maintainer action.
update_docs = os.environ.get("KAIRO_UPDATE_DOC_IMAGE") == "1"
render_output = (
    repository / "docs" / "images" / "blender-asset-result.png"
    if update_docs
    else project / "blender-asset-result.png"
)
scene.render.filepath = str(render_output)
scene.render.film_transparent = False
scene.world.color = (0.008, 0.012, 0.025)

bpy.ops.object.select_all(action="DESELECT")
crate.select_set(True)
bpy.context.view_layer.objects.active = crate

scene_path = sources / "WorkshopCrate.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(scene_path), check_existing=False)
settings = bpy.context.scene.kairo_pipeline
settings.project_root = str(project)
settings.project_name = "Portfolio"
settings.asset_name = "WorkshopCrate"
settings.version = 1
settings.scope = "SELECTED"
bpy.ops.kairo.validate()
bpy.ops.wm.save_as_mainfile(filepath=str(scene_path), check_existing=False)
bpy.ops.render.render(write_still=True)
print(scene_path)
print(render_output)
