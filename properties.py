"""Persistent Blender scene settings for the Kairo pipeline."""

from __future__ import annotations

import bpy


class KairoDiagnosticItem(bpy.types.PropertyGroup):
    """UI-safe copy of one structured pipeline diagnostic."""

    code: bpy.props.StringProperty()
    severity: bpy.props.StringProperty()
    message: bpy.props.StringProperty()
    suggestion: bpy.props.StringProperty()
    object_name: bpy.props.StringProperty()
    property_name: bpy.props.StringProperty()


class KairoProjectSettings(bpy.types.PropertyGroup):
    """Artist-authored destination and version for the next publish."""

    project_root: bpy.props.StringProperty(
        name="Project Root",
        description="Root directory containing the Kairo project",
        subtype="DIR_PATH",
    )
    project_name: bpy.props.StringProperty(
        name="Project",
        description="Portable production project identifier",
        default="Portfolio",
    )
    asset_name: bpy.props.StringProperty(
        name="Asset",
        description="Portable asset identifier used by publish versions",
        default="UntitledAsset",
    )
    version: bpy.props.IntProperty(
        name="Version",
        description="Immutable publish version",
        default=1,
        min=1,
        max=999_999,
    )
    scope: bpy.props.EnumProperty(
        name="Scope",
        description="Objects inspected and exported by the pipeline",
        items=(
            ("SELECTED", "Selected Objects", "Use the current object selection"),
            ("SCENE", "Complete Scene", "Use every object in the active scene"),
        ),
        default="SELECTED",
    )
    polygon_budget: bpy.props.IntProperty(
        name="Polygon Budget",
        description="Warn when the publish set exceeds this polygon count",
        default=500_000,
        min=1,
        max=100_000_000,
    )
    diagnostics: bpy.props.CollectionProperty(type=KairoDiagnosticItem)
    last_summary: bpy.props.StringProperty(default="Not validated")
