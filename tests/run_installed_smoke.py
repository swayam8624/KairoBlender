# TEACHING MAP — tests/run_installed_smoke.py
# Smoke checks the packaged extension in an installed Blender host. Confirms
# installation/registration separately from unit-level validators.
# Read READING_ORDER.md; original bridge code retains GPL-3.0-or-later.

"""Verify the packaged extension is enabled and exposes its artist UI state."""

from __future__ import annotations

import bpy


if not hasattr(bpy.types.Scene, "kairo_pipeline"):
    raise RuntimeError("installed Kairo Blender extension is not enabled")
settings = bpy.context.scene.kairo_pipeline
if settings.project_name != "Portfolio" or settings.version != 1:
    raise RuntimeError("installed extension settings did not initialize correctly")
print("KAIRO_BLENDER_INSTALLED_SMOKE_OK")

