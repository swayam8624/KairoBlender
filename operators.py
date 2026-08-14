"""Interactive validation and diagnostic navigation operators."""

from __future__ import annotations

import bpy

from .adapter import snapshot_scene
from .validation import ValidationProfile, validate_scene


class KAIRO_OT_validate(bpy.types.Operator):
    bl_idname = "kairo.validate"
    bl_label = "Validate for Kairo"
    bl_description = "Inspect the publish set and report production blockers"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        settings = context.scene.kairo_pipeline
        settings.diagnostics.clear()
        try:
            scene = snapshot_scene(
                context,
                selected_only=settings.scope == "SELECTED",
            )
            diagnostics = validate_scene(
                scene,
                ValidationProfile(polygon_budget=settings.polygon_budget),
            )
            for diagnostic in diagnostics:
                item = settings.diagnostics.add()
                item.code = diagnostic.code
                item.severity = diagnostic.severity.value
                item.message = diagnostic.message
                item.suggestion = diagnostic.suggestion
                if diagnostic.location is not None:
                    item.object_name = diagnostic.location.object_path
                    item.property_name = diagnostic.location.property_name
            errors = sum(item.severity == "error" for item in settings.diagnostics)
            warnings = sum(item.severity == "warning" for item in settings.diagnostics)
            settings.last_summary = (
                f"{errors} error(s), {warnings} warning(s), "
                f"{len(settings.diagnostics)} total"
            )
            if errors:
                self.report(
                    {"WARNING"},
                    f"Kairo validation blocked: {settings.last_summary}",
                )
            else:
                self.report({"INFO"}, f"Kairo validation passed: {settings.last_summary}")
            return {"FINISHED"}
        except (OSError, TypeError, ValueError, RuntimeError) as error:
            settings.last_summary = f"Validation failed: {error}"
            self.report({"ERROR"}, settings.last_summary)
            return {"CANCELLED"}


class KAIRO_OT_select_diagnostic(bpy.types.Operator):
    bl_idname = "kairo.select_diagnostic"
    bl_label = "Select Problem"
    bl_description = "Select the Blender object referenced by this diagnostic"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set[str]:
        diagnostics = context.scene.kairo_pipeline.diagnostics
        if self.index < 0 or self.index >= len(diagnostics):
            self.report({"ERROR"}, "Diagnostic index is no longer valid")
            return {"CANCELLED"}
        target_name = diagnostics[self.index].object_name
        target = context.scene.objects.get(target_name)
        if target is None:
            self.report({"WARNING"}, "Diagnostic does not reference an available object")
            return {"CANCELLED"}
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
        context.view_layer.objects.active = target
        return {"FINISHED"}


class KAIRO_OT_clear_diagnostics(bpy.types.Operator):
    bl_idname = "kairo.clear_diagnostics"
    bl_label = "Clear Diagnostics"
    bl_options = {"INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        settings = context.scene.kairo_pipeline
        settings.diagnostics.clear()
        settings.last_summary = "Not validated"
        return {"FINISHED"}
