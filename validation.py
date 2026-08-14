"""Pure scene snapshots and validation rules for Blender publishing."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable

from kairo_pipeline.diagnostics import (
    Diagnostic,
    DiagnosticBag,
    DiagnosticLocation,
    Severity,
)


_PORTABLE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SUPPORTED_OBJECT_TYPES = frozenset({"MESH", "EMPTY"})


@dataclass(frozen=True, slots=True)
class ImageSnapshot:
    name: str
    path: str
    exists: bool
    packed: bool
    color_space: str


@dataclass(frozen=True, slots=True)
class MaterialSnapshot:
    name: str
    uses_nodes: bool
    has_output: bool
    has_principled: bool
    images: tuple[ImageSnapshot, ...] = ()


@dataclass(frozen=True, slots=True)
class MeshSnapshot:
    vertices: int
    edges: int
    polygons: int
    uv_layers: int
    degenerate_polygons: int
    materials: tuple[MaterialSnapshot, ...] = ()


@dataclass(frozen=True, slots=True)
class ObjectSnapshot:
    name: str
    object_type: str
    hidden_from_render: bool
    scale: tuple[float, float, float]
    rotation: tuple[float, float, float]
    mesh: MeshSnapshot | None = None


@dataclass(frozen=True, slots=True)
class SceneSnapshot:
    source_path: str
    objects: tuple[ObjectSnapshot, ...]


@dataclass(frozen=True, slots=True)
class ValidationProfile:
    require_uv: bool = True
    require_material: bool = True
    polygon_budget: int = 500_000

    def __post_init__(self) -> None:
        if self.polygon_budget < 1:
            raise ValueError("polygon budget must be positive")


def validate_scene(
    scene: SceneSnapshot,
    profile: ValidationProfile = ValidationProfile(),
) -> DiagnosticBag:
    """Validate one immutable scene snapshot for deterministic static export."""

    if not isinstance(scene, SceneSnapshot):
        raise TypeError("scene must be SceneSnapshot")
    if not isinstance(profile, ValidationProfile):
        raise TypeError("profile must be ValidationProfile")

    diagnostics = DiagnosticBag()
    if not scene.source_path:
        diagnostics.add(
            Diagnostic(
                "SCENE_UNSAVED",
                Severity.ERROR,
                "Save the Blender scene before publishing.",
                DiagnosticLocation(host="blender"),
                "Save the .blend file into the project source directory.",
            )
        )
    if not scene.objects:
        diagnostics.add(
            Diagnostic(
                "SCENE_EMPTY",
                Severity.ERROR,
                "The scene contains no publishable objects.",
                DiagnosticLocation(host="blender", resource=scene.source_path),
            )
        )
        return diagnostics

    names: dict[str, str] = {}
    total_polygons = 0
    for item in scene.objects:
        location = DiagnosticLocation(
            host="blender",
            resource=scene.source_path,
            object_path=item.name,
        )
        if not _PORTABLE_NAME.fullmatch(item.name):
            diagnostics.add(
                Diagnostic(
                    "OBJECT_NAME_PORTABILITY",
                    Severity.WARNING,
                    f"Object name is not a portable identifier: {item.name}",
                    location,
                    "Use letters, digits, dots, underscores, or hyphens.",
                )
            )
        key = item.name.casefold()
        if key in names:
            diagnostics.add(
                Diagnostic(
                    "OBJECT_NAME_COLLISION",
                    Severity.ERROR,
                    f"Object name collides case-insensitively with {names[key]}.",
                    location,
                    "Rename one object so the names remain unique on every platform.",
                )
            )
        else:
            names[key] = item.name

        if item.object_type not in _SUPPORTED_OBJECT_TYPES:
            diagnostics.add(
                Diagnostic(
                    "OBJECT_TYPE_UNSUPPORTED",
                    Severity.ERROR,
                    f"Object type {item.object_type} is not supported by the static asset profile.",
                    location,
                    "Convert the result to a mesh or exclude the object from publishing.",
                )
            )
            continue
        if item.hidden_from_render:
            diagnostics.add(
                Diagnostic(
                    "OBJECT_RENDER_HIDDEN",
                    Severity.WARNING,
                    "Object is disabled for rendering but included in the publish set.",
                    location,
                )
            )
        _validate_transform(item, location, diagnostics)
        if item.object_type == "MESH":
            if item.mesh is None:
                diagnostics.add(
                    Diagnostic(
                        "MESH_DATA_MISSING",
                        Severity.ERROR,
                        "Mesh object has no mesh data.",
                        location,
                    )
                )
                continue
            total_polygons += item.mesh.polygons
            _validate_mesh(item.mesh, location, profile, diagnostics)

    if total_polygons > profile.polygon_budget:
        diagnostics.add(
            Diagnostic(
                "SCENE_POLYGON_BUDGET",
                Severity.WARNING,
                f"Scene contains {total_polygons} polygons; profile budget is {profile.polygon_budget}.",
                DiagnosticLocation(host="blender", resource=scene.source_path),
                "Reduce source complexity or choose an approved higher-budget profile.",
            )
        )
    return diagnostics


def _validate_transform(
    item: ObjectSnapshot,
    location: DiagnosticLocation,
    diagnostics: DiagnosticBag,
) -> None:
    transform_values = (*item.scale, *item.rotation)
    if not all(math.isfinite(value) for value in transform_values):
        diagnostics.add(
            Diagnostic(
                "OBJECT_TRANSFORM_NONFINITE",
                Severity.ERROR,
                "Object transform contains a non-finite value.",
                location,
            )
        )
        return
    if any(value < 0.0 for value in item.scale):
        diagnostics.add(
            Diagnostic(
                "OBJECT_SCALE_NEGATIVE",
                Severity.ERROR,
                "Object has a negative scale that may invert winding or tangents.",
                location,
                "Apply or correct the scale and verify normals before publishing.",
            )
        )
    if max(item.scale) - min(item.scale) > 1.0e-5:
        diagnostics.add(
            Diagnostic(
                "OBJECT_SCALE_NONUNIFORM",
                Severity.WARNING,
                "Object has non-uniform scale.",
                location,
                "Apply scale when the deformation is intentional.",
            )
        )
    if any(abs(value - 1.0) > 1.0e-5 for value in item.scale):
        diagnostics.add(
            Diagnostic(
                "OBJECT_SCALE_UNAPPLIED",
                Severity.WARNING,
                "Object scale is not applied.",
                location,
                "Apply scale before publishing a reusable asset.",
            )
        )


def _validate_mesh(
    mesh: MeshSnapshot,
    location: DiagnosticLocation,
    profile: ValidationProfile,
    diagnostics: DiagnosticBag,
) -> None:
    if mesh.vertices < 3 or mesh.polygons < 1:
        diagnostics.add(
            Diagnostic(
                "MESH_EMPTY",
                Severity.ERROR,
                "Mesh contains no renderable polygon geometry.",
                location,
            )
        )
    if mesh.degenerate_polygons:
        diagnostics.add(
            Diagnostic(
                "MESH_DEGENERATE_POLYGONS",
                Severity.ERROR,
                f"Mesh contains {mesh.degenerate_polygons} zero-area polygons.",
                location,
                "Remove or rebuild degenerate faces before export.",
            )
        )
    if profile.require_uv and mesh.uv_layers < 1:
        diagnostics.add(
            Diagnostic(
                "MESH_UV_MISSING",
                Severity.ERROR,
                "Mesh has no UV map for the production material profile.",
                location,
                "Create and inspect a primary UV map.",
            )
        )
    if profile.require_material and not mesh.materials:
        diagnostics.add(
            Diagnostic(
                "MESH_MATERIAL_MISSING",
                Severity.ERROR,
                "Mesh has no assigned material.",
                location,
                "Assign a supported Principled BSDF material.",
            )
        )
    for material in mesh.materials:
        _validate_material(material, location, diagnostics)


def _validate_material(
    material: MaterialSnapshot,
    location: DiagnosticLocation,
    diagnostics: DiagnosticBag,
) -> None:
    material_location = DiagnosticLocation(
        host=location.host,
        resource=location.resource,
        object_path=location.object_path,
        property_name=f"material:{material.name}",
    )
    if not material.uses_nodes or not material.has_output:
        diagnostics.add(
            Diagnostic(
                "MATERIAL_OUTPUT_MISSING",
                Severity.ERROR,
                f"Material {material.name} has no usable surface output.",
                material_location,
            )
        )
    if not material.has_principled:
        diagnostics.add(
            Diagnostic(
                "MATERIAL_SHADER_UNSUPPORTED",
                Severity.ERROR,
                f"Material {material.name} does not use a Principled BSDF shader.",
                material_location,
                "Bake or convert the material to the supported metallic/roughness profile.",
            )
        )
    for image in material.images:
        if not image.packed and not image.exists:
            diagnostics.add(
                Diagnostic(
                    "TEXTURE_FILE_MISSING",
                    Severity.ERROR,
                    f"Texture file is missing: {image.path or image.name}",
                    DiagnosticLocation(
                        host=location.host,
                        resource=location.resource,
                        object_path=location.object_path,
                        property_name=f"image:{image.name}",
                    ),
                    "Relink or pack the image before publishing.",
                )
            )


def blocking_codes(diagnostics: Iterable[Diagnostic]) -> tuple[str, ...]:
    """Return deterministic error codes for UI summaries and headless gates."""

    return tuple(item.code for item in diagnostics if item.blocks_publish)

