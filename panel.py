"""Blender 3D View user interface for the Kairo workflow."""

from __future__ import annotations

import bpy


class KAIRO_PT_pipeline(bpy.types.Panel):
    bl_idname = "KAIRO_PT_pipeline"
    bl_label = "Kairo Pipeline"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Kairo"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        settings = context.scene.kairo_pipeline
        layout.prop(settings, "project_root")
        layout.prop(settings, "project_name")
        layout.prop(settings, "asset_name")
        layout.prop(settings, "version")
        box = layout.box()
        box.label(text="Validation and publishing arrive in the next increments")

