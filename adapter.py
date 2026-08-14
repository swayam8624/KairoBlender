"""Translation from Blender data blocks into immutable validation snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import bpy

from .validation import (
    ImageSnapshot,
    MaterialSnapshot,
    MeshSnapshot,
    ObjectSnapshot,
    SceneSnapshot,
)


def snapshot_scene(
    context: bpy.types.Context,
    *,
    selected_only: bool,
) -> SceneSnapshot:
    """Capture the current scene without retaining mutable Blender references."""

    source = bpy.data.filepath
    objects: Iterable[bpy.types.Object]
    if selected_only:
        objects = context.selected_objects
    else:
        objects = context.scene.objects
    snapshots = tuple(
        _snapshot_object(item)
        for item in sorted(objects, key=lambda candidate: candidate.name.casefold())
    )
    return SceneSnapshot(source_path=source, objects=snapshots)


def _snapshot_object(item: bpy.types.Object) -> ObjectSnapshot:
    mesh = _snapshot_mesh(item.data) if item.type == "MESH" and item.data else None
    return ObjectSnapshot(
        name=item.name,
        object_type=item.type,
        hidden_from_render=item.hide_render,
        scale=tuple(float(value) for value in item.scale),
        rotation=tuple(float(value) for value in item.rotation_euler),
        mesh=mesh,
    )


def _snapshot_mesh(mesh: bpy.types.Mesh) -> MeshSnapshot:
    materials = tuple(
        _snapshot_material(material)
        for material in mesh.materials
        if material is not None
    )
    return MeshSnapshot(
        vertices=len(mesh.vertices),
        edges=len(mesh.edges),
        polygons=len(mesh.polygons),
        uv_layers=len(mesh.uv_layers),
        degenerate_polygons=sum(1 for polygon in mesh.polygons if polygon.area <= 1.0e-12),
        materials=materials,
    )


def _snapshot_material(material: bpy.types.Material) -> MaterialSnapshot:
    nodes = tuple(material.node_tree.nodes) if material.use_nodes and material.node_tree else ()
    images: list[ImageSnapshot] = []
    for node in nodes:
        if node.type != "TEX_IMAGE" or node.image is None:
            continue
        image = node.image
        resolved = bpy.path.abspath(image.filepath) if image.filepath else ""
        images.append(
            ImageSnapshot(
                name=image.name,
                path=image.filepath,
                exists=bool(resolved and Path(resolved).is_file()),
                packed=image.packed_file is not None,
                color_space=image.colorspace_settings.name,
            )
        )
    return MaterialSnapshot(
        name=material.name,
        uses_nodes=material.use_nodes,
        has_output=any(
            node.type == "OUTPUT_MATERIAL"
            and node.inputs.get("Surface") is not None
            and node.inputs["Surface"].is_linked
            for node in nodes
        ),
        has_principled=any(node.type == "BSDF_PRINCIPLED" for node in nodes),
        images=tuple(sorted(images, key=lambda image: image.name.casefold())),
    )

