"""Native Blender smoke tests executed in a factory-startup process."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY.parent))


class ExtensionRegistrationTests(unittest.TestCase):
    def test_register_and_unregister_extension(self) -> None:
        import bpy

        extension = importlib.import_module(REPOSITORY.name)
        extension.register()
        try:
            self.assertTrue(hasattr(bpy.types.Scene, "kairo_pipeline"))
            settings = bpy.context.scene.kairo_pipeline
            self.assertEqual(settings.project_name, "Portfolio")
            self.assertEqual(settings.asset_name, "UntitledAsset")
            self.assertEqual(settings.version, 1)
        finally:
            extension.unregister()
        self.assertFalse(hasattr(bpy.types.Scene, "kairo_pipeline"))


suite = unittest.defaultTestLoader.loadTestsFromTestCase(
    ExtensionRegistrationTests
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)

