"""Interactive validation and diagnostic navigation operators."""

from __future__ import annotations

import bpy
import re
from pathlib import Path

from .adapter import snapshot_scene
from .publisher import export_and_publish
from .validation import ValidationProfile, validate_scene


_FIXABLE_CODES = frozenset(
    {
        "OBJECT_NAME_PORTABILITY",
        "OBJECT_RENDER_HIDDEN",
        "OBJECT_SCALE_NONUNIFORM",
        "OBJECT_SCALE_UNAPPLIED",
    }
)


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
                item.fixable = diagnostic.code in _FIXABLE_CODES
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


class KAIRO_OT_fix_diagnostic(bpy.types.Operator):
    bl_idname = "kairo.fix_diagnostic"
    bl_label = "Apply Safe Fix"
    bl_description = "Apply the bounded automatic repair for this diagnostic"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set[str]:
        settings = context.scene.kairo_pipeline
        if self.index < 0 or self.index >= len(settings.diagnostics):
            self.report({"ERROR"}, "Diagnostic index is no longer valid")
            return {"CANCELLED"}
        diagnostic = settings.diagnostics[self.index]
        target = context.scene.objects.get(diagnostic.object_name)
        if target is None:
            self.report({"ERROR"}, "Safe fix requires an available object")
            return {"CANCELLED"}

        if diagnostic.code == "OBJECT_RENDER_HIDDEN":
            target.hide_render = False
        elif diagnostic.code in {
            "OBJECT_SCALE_NONUNIFORM",
            "OBJECT_SCALE_UNAPPLIED",
        }:
            if target.mode != "OBJECT":
                self.report({"ERROR"}, "Apply scale from Object mode")
                return {"CANCELLED"}
            with context.temp_override(
                active_object=target,
                object=target,
                selected_objects=[target],
                selected_editable_objects=[target],
            ):
                result = bpy.ops.object.transform_apply(
                    location=False,
                    rotation=False,
                    scale=True,
                )
            if result != {"FINISHED"}:
                self.report({"ERROR"}, "Blender could not apply object scale")
                return {"CANCELLED"}
        elif diagnostic.code == "OBJECT_NAME_PORTABILITY":
            target.name = _portable_unique_name(context.scene, target)
        else:
            self.report({"ERROR"}, "This diagnostic has no safe automatic fix")
            return {"CANCELLED"}

        bpy.ops.kairo.validate()
        return {"FINISHED"}


def _portable_unique_name(
    scene: bpy.types.Scene,
    target: bpy.types.Object,
) -> str:
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", target.name).strip("._-")
    if not base:
        base = "Object"
    base = base[:128]
    occupied = {
        item.name.casefold()
        for item in scene.objects
        if item != target
    }
    if base.casefold() not in occupied:
        return base
    for suffix in range(1, 100_000):
        suffix_text = f"_{suffix}"
        candidate = f"{base[: 128 - len(suffix_text)]}{suffix_text}"
        if candidate.casefold() not in occupied:
            return candidate
    raise RuntimeError("could not create a unique portable object name")


class KAIRO_OT_publish(bpy.types.Operator):
    bl_idname = "kairo.publish"
    bl_label = "Publish to Kairo"
    bl_description = "Validate, export, fingerprint, and atomically publish the asset"
    bl_options = {"REGISTER"}

    dry_run: bpy.props.BoolProperty(default=False)

    def execute(self, context: bpy.types.Context) -> set[str]:
        settings = context.scene.kairo_pipeline
        validation_result = bpy.ops.kairo.validate()
        if validation_result != {"FINISHED"}:
            return {"CANCELLED"}
        if any(item.severity == "error" for item in settings.diagnostics):
            self.report({"WARNING"}, "Resolve blocking diagnostics before publishing")
            return {"CANCELLED"}
        try:
            result = export_and_publish(
                context,
                project_root=Path(bpy.path.abspath(settings.project_root)),
                project_name=settings.project_name,
                asset_name=settings.asset_name,
                version=settings.version,
                selected_only=settings.scope == "SELECTED",
                dry_run=self.dry_run,
                replace=settings.replace_existing,
            )
            settings.last_publish_target = str(result.target)
            settings.last_publish_hash = result.manifest_sha256
            settings.last_summary = (
                f"{'Planned' if result.dry_run else 'Published'} "
                f"{result.files} file(s), {result.bytes} bytes"
            )
            self.report({"INFO"}, settings.last_summary)
            return {"FINISHED"}
        except (FileExistsError, FileNotFoundError, NotADirectoryError, ValueError) as error:
            # These are expected, user-correctable publication rejections.
            # Blender escalates ERROR reports from bpy.ops into RuntimeError,
            # so report them as warnings and preserve the operator's CANCELLED
            # contract for scripts/tests/UI callers.
            settings.last_summary = f"Publish blocked: {error}"
            self.report({"WARNING"}, settings.last_summary)
            return {"CANCELLED"}
        except RuntimeError as error:
            # Unsaved-scene provenance rejection is also expected. Other
            # RuntimeError instances are treated as internal failures below.
            if "save Blender scene changes before publishing" in str(error):
                settings.last_summary = f"Publish blocked: {error}"
                self.report({"WARNING"}, settings.last_summary)
                return {"CANCELLED"}
            settings.last_summary = f"Publish failed: {error}"
            self.report({"ERROR"}, settings.last_summary)
            return {"CANCELLED"}
        except OSError as error:
            settings.last_summary = f"Publish failed: {error}"
            self.report({"ERROR"}, settings.last_summary)
            return {"CANCELLED"}
