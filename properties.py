"""Persistent Blender scene settings for the Kairo pipeline."""

from __future__ import annotations

import bpy


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

