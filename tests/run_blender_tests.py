"""Native Blender smoke tests executed in a factory-startup process."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY.parent))
sys.path.insert(0, str(REPOSITORY.parent / "KairoPipelineCore" / "src"))


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

    def test_validation_operator_reports_and_navigates_mesh_problem(self) -> None:
        import bpy

        extension = importlib.import_module(REPOSITORY.name)
        extension.register()
        try:
            bpy.ops.object.select_all(action="DESELECT")
            cube = bpy.context.scene.objects["Cube"]
            cube.data.materials.clear()
            while cube.data.uv_layers:
                cube.data.uv_layers.remove(cube.data.uv_layers[0])
            cube.select_set(True)
            bpy.context.view_layer.objects.active = cube
            result = bpy.ops.kairo.validate()
            self.assertEqual(result, {"FINISHED"})
            settings = bpy.context.scene.kairo_pipeline
            codes = {item.code for item in settings.diagnostics}
            self.assertIn("SCENE_UNSAVED", codes)
            self.assertIn("MESH_MATERIAL_MISSING", codes)
            target_index = next(
                index
                for index, item in enumerate(settings.diagnostics)
                if item.object_name == "Cube"
            )
            bpy.ops.object.select_all(action="DESELECT")
            result = bpy.ops.kairo.select_diagnostic(index=target_index)
            self.assertEqual(result, {"FINISHED"})
            self.assertEqual(bpy.context.view_layer.objects.active.name, "Cube")
        finally:
            extension.unregister()


suite = unittest.defaultTestLoader.loadTestsFromTestCase(
    ExtensionRegistrationTests
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
