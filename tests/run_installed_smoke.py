# SOURCE STUDY NOTE:
# Post-install Blender extension smoke test verifying registration/integration in host runtime,
# separate from build archive generation.
# Follow docs/SOURCE_READING_ORDER.md for native-host vs portable tests.

"""Verify the packaged extension is enabled and exposes its artist UI state."""

from __future__ import annotations

import bpy


if not hasattr(bpy.types.Scene, "kairo_pipeline"):
    raise RuntimeError("installed Kairo Blender extension is not enabled")
settings = bpy.context.scene.kairo_pipeline
if settings.project_name != "Portfolio" or settings.version != 1:
    raise RuntimeError("installed extension settings did not initialize correctly")
print("KAIRO_BLENDER_INSTALLED_SMOKE_OK")

