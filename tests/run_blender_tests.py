"""Native Blender smoke tests executed in a factory-startup process."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY.parent))
sys.path.insert(0, str(REPOSITORY.parent / "KairoPipelineCore" / "src"))


class ExtensionRegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        import bpy

        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        cube.name = "Cube"
        if not cube.data.uv_layers:
            cube.data.uv_layers.new(name="UVMap")
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        cube.data.materials.append(material)

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

    def test_safe_fix_applies_scale_and_revalidates(self) -> None:
        import bpy

        extension = importlib.import_module(REPOSITORY.name)
        extension.register()
        try:
            bpy.ops.object.select_all(action="DESELECT")
            cube = bpy.context.scene.objects["Cube"]
            cube.scale = (2.0, 1.0, 1.0)
            cube.select_set(True)
            bpy.context.view_layer.objects.active = cube
            bpy.ops.kairo.validate()
            settings = bpy.context.scene.kairo_pipeline
            fix_index = next(
                index
                for index, item in enumerate(settings.diagnostics)
                if item.code == "OBJECT_SCALE_UNAPPLIED"
            )
            result = bpy.ops.kairo.fix_diagnostic(index=fix_index)
            self.assertEqual(result, {"FINISHED"})
            self.assertEqual(tuple(cube.scale), (1.0, 1.0, 1.0))
            self.assertNotIn(
                "OBJECT_SCALE_UNAPPLIED",
                {item.code for item in settings.diagnostics},
            )
        finally:
            extension.unregister()

    def test_real_gltf_export_is_atomically_published(self) -> None:
        import bpy

        extension = importlib.import_module(REPOSITORY.name)
        extension.register()
        try:
            with tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                sources = project / "sources"
                sources.mkdir()
                bpy.ops.wm.save_as_mainfile(
                    filepath=str(sources / "chair.blend"),
                    check_existing=False,
                )
                settings = bpy.context.scene.kairo_pipeline
                settings.project_root = str(project)
                settings.project_name = "Portfolio"
                settings.asset_name = "Chair"
                settings.version = 1
                settings.scope = "SELECTED"

                dry_run = bpy.ops.kairo.publish(dry_run=True)
                self.assertEqual(dry_run, {"FINISHED"})
                self.assertFalse((project / "Published").exists())

                published = bpy.ops.kairo.publish(dry_run=False)
                self.assertEqual(published, {"FINISHED"})
                target = Path(settings.last_publish_target)
                self.assertTrue((target / "geometry/Chair.gltf").is_file())
                self.assertTrue((target / "geometry/Chair.bin").is_file())
                self.assertTrue((target / "publish.kairo.json").is_file())
                self.assertEqual(len(settings.last_publish_hash), 64)
        finally:
            extension.unregister()


suite = unittest.defaultTestLoader.loadTestsFromTestCase(
    ExtensionRegistrationTests
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
