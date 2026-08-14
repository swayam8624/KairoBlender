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
        layout.prop(settings, "scope")
        layout.prop(settings, "polygon_budget")
        row = layout.row(align=True)
        row.operator("kairo.validate", icon="CHECKMARK")
        row.operator("kairo.clear_diagnostics", text="", icon="X")
        layout.label(text=settings.last_summary)
        for index, diagnostic in enumerate(settings.diagnostics):
            box = layout.box()
            row = box.row(align=True)
            icon = {
                "error": "ERROR",
                "warning": "ERROR",
                "info": "INFO",
            }.get(diagnostic.severity, "QUESTION")
            row.label(text=diagnostic.code, icon=icon)
            if diagnostic.object_name:
                operator = row.operator(
                    "kairo.select_diagnostic",
                    text="Select",
                    icon="RESTRICT_SELECT_OFF",
                )
                operator.index = index
            box.label(text=diagnostic.message)
            if diagnostic.suggestion:
                box.label(text=diagnostic.suggestion, icon="LIGHTBULB")
