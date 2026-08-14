"""Kairo artist-facing validation and publishing extension for Blender."""

from __future__ import annotations

import bpy

from .panel import KAIRO_PT_pipeline
from .properties import KairoProjectSettings


_CLASSES = (
    KairoProjectSettings,
    KAIRO_PT_pipeline,
)


def register() -> None:
    """Register the extension's public Blender types."""

    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.kairo_pipeline = bpy.props.PointerProperty(
        type=KairoProjectSettings
    )


def unregister() -> None:
    """Remove the extension without leaving scene-level RNA properties."""

    if hasattr(bpy.types.Scene, "kairo_pipeline"):
        del bpy.types.Scene.kairo_pipeline
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)

