from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))
sys.path.insert(0, str(REPOSITORY.parent / "KairoPipelineCore" / "src"))

from validation import (  # noqa: E402
    ImageSnapshot,
    MaterialSnapshot,
    MeshSnapshot,
    ObjectSnapshot,
    SceneSnapshot,
    ValidationProfile,
    blocking_codes,
    validate_scene,
)


def valid_material() -> MaterialSnapshot:
    return MaterialSnapshot(
        name="Paint",
        uses_nodes=True,
        has_output=True,
        has_principled=True,
        images=(
            ImageSnapshot(
                name="PaintBaseColor",
                path="//textures/paint.png",
                exists=True,
                packed=False,
                color_space="sRGB",
            ),
        ),
    )


def valid_mesh() -> MeshSnapshot:
    return MeshSnapshot(
        vertices=8,
        edges=12,
        polygons=6,
        uv_layers=1,
        degenerate_polygons=0,
        materials=(valid_material(),),
    )


class ValidationTests(unittest.TestCase):
    def test_valid_static_mesh_has_no_diagnostics(self) -> None:
        scene = SceneSnapshot(
            source_path="/project/chair.blend",
            objects=(
                ObjectSnapshot(
                    name="Chair",
                    object_type="MESH",
                    hidden_from_render=False,
                    scale=(1.0, 1.0, 1.0),
                    rotation=(0.0, 0.0, 0.0),
                    mesh=valid_mesh(),
                ),
            ),
        )
        self.assertEqual(tuple(validate_scene(scene)), ())

    def test_broken_scene_reports_actionable_failures(self) -> None:
        scene = SceneSnapshot(
            source_path="",
            objects=(
                ObjectSnapshot(
                    name="Broken Chair",
                    object_type="MESH",
                    hidden_from_render=True,
                    scale=(-1.0, 2.0, 1.0),
                    rotation=(0.0, 0.0, 0.0),
                    mesh=MeshSnapshot(
                        vertices=3,
                        edges=3,
                        polygons=1,
                        uv_layers=0,
                        degenerate_polygons=1,
                        materials=(
                            MaterialSnapshot(
                                name="Broken",
                                uses_nodes=False,
                                has_output=False,
                                has_principled=False,
                                images=(
                                    ImageSnapshot(
                                        name="Missing",
                                        path="//missing.png",
                                        exists=False,
                                        packed=False,
                                        color_space="sRGB",
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
        diagnostics = validate_scene(scene)
        codes = {item.code for item in diagnostics}
        self.assertIn("SCENE_UNSAVED", codes)
        self.assertIn("OBJECT_SCALE_NEGATIVE", codes)
        self.assertIn("MESH_DEGENERATE_POLYGONS", codes)
        self.assertIn("MESH_UV_MISSING", codes)
        self.assertIn("MATERIAL_SHADER_UNSUPPORTED", codes)
        self.assertIn("TEXTURE_FILE_MISSING", codes)
        self.assertTrue(diagnostics.blocks_publish)

    def test_case_collisions_and_budget_are_reported(self) -> None:
        objects = tuple(
            ObjectSnapshot(
                name=name,
                object_type="MESH",
                hidden_from_render=False,
                scale=(1.0, 1.0, 1.0),
                rotation=(0.0, 0.0, 0.0),
                mesh=valid_mesh(),
            )
            for name in ("Chair", "chair")
        )
        diagnostics = validate_scene(
            SceneSnapshot("scene.blend", objects),
            ValidationProfile(polygon_budget=10),
        )
        codes = {item.code for item in diagnostics}
        self.assertIn("OBJECT_NAME_COLLISION", codes)
        self.assertIn("SCENE_POLYGON_BUDGET", codes)

    def test_blocking_codes_excludes_warnings(self) -> None:
        scene = SceneSnapshot(
            "scene.blend",
            (
                ObjectSnapshot(
                    "Chair",
                    "MESH",
                    True,
                    (1.0, 1.0, 1.0),
                    (0.0, 0.0, 0.0),
                    valid_mesh(),
                ),
            ),
        )
        self.assertEqual(blocking_codes(validate_scene(scene)), ())


if __name__ == "__main__":
    unittest.main()
