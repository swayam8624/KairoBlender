"""Deterministic Blender export and atomic production publication."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

import bpy

from kairo_pipeline.fingerprint import fingerprint_file
from kairo_pipeline.manifest import PublishFile, PublishKind, PublishManifest
from kairo_pipeline.publish import plan_publish, publish_bundle


@dataclass(frozen=True, slots=True)
class BlenderPublishResult:
    target: Path
    files: int
    bytes: int
    manifest_sha256: str
    dry_run: bool


def export_and_publish(
    context: bpy.types.Context,
    *,
    project_root: Path,
    project_name: str,
    asset_name: str,
    version: int,
    selected_only: bool,
    dry_run: bool,
    replace: bool,
) -> BlenderPublishResult:
    """Export one static glTF source package and publish it atomically."""

    root = Path(project_root).expanduser().resolve(strict=False)
    if not root.is_dir():
        raise NotADirectoryError(f"Kairo project root is not a directory: {root}")
    blend_path = Path(bpy.data.filepath)
    if not blend_path.is_file():
        raise FileNotFoundError("save the Blender scene before publishing")
    try:
        source_path = blend_path.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise ValueError(
            "the Blender scene must be saved inside the selected project root"
        ) from error
    if selected_only and not context.selected_objects:
        raise ValueError("select at least one object before publishing")

    with tempfile.TemporaryDirectory(prefix="kairo-blender-export-") as directory:
        staging = Path(directory)
        geometry = staging / "geometry"
        geometry.mkdir()
        gltf_path = geometry / f"{asset_name}.gltf"
        result = bpy.ops.export_scene.gltf(
            filepath=str(gltf_path),
            check_existing=False,
            export_format="GLTF_SEPARATE",
            export_texture_dir="textures",
            export_texcoords=True,
            export_normals=True,
            export_tangents=True,
            export_materials="EXPORT",
            export_animations=False,
            export_cameras=False,
            export_lights=False,
            use_selection=selected_only,
        )
        if result != {"FINISHED"} or not gltf_path.is_file():
            raise RuntimeError("Blender glTF export did not produce the expected scene")

        exported = tuple(
            sorted(
                (path for path in staging.rglob("*") if path.is_file()),
                key=lambda path: path.relative_to(staging).as_posix().casefold(),
            )
        )
        outputs = (
            _publish_file(staging, gltf_path, role="scene", media_type="model/gltf+json"),
        )
        dependencies = tuple(
            _publish_file(
                staging,
                path,
                role=_dependency_role(path),
                media_type=_media_type(path),
            )
            for path in exported
            if path != gltf_path
        )
        manifest = PublishManifest(
            kind=PublishKind.ASSET,
            project=project_name,
            name=asset_name,
            version=version,
            source_host="blender",
            source_path=source_path,
            source_fingerprint=fingerprint_file(blend_path),
            outputs=outputs,
            dependencies=dependencies,
            metadata={
                "blender_version": bpy.app.version_string,
                "export_format": "gltf-separate",
                "scope": "selected" if selected_only else "scene",
            },
        )
        library = root / "Published"
        if dry_run:
            plan = plan_publish(staging, library, manifest, replace=replace)
            return BlenderPublishResult(
                target=plan.target,
                files=len(plan.files),
                bytes=sum(item.fingerprint.size for item in plan.files),
                manifest_sha256=plan.manifest_fingerprint.sha256,
                dry_run=True,
            )
        published = publish_bundle(staging, library, manifest, replace=replace)
        return BlenderPublishResult(
            target=published.target,
            files=published.copied_files,
            bytes=published.copied_bytes,
            manifest_sha256=published.manifest_fingerprint.sha256,
            dry_run=False,
        )


def _publish_file(
    staging: Path,
    path: Path,
    *,
    role: str,
    media_type: str,
) -> PublishFile:
    return PublishFile(
        path=path.relative_to(staging).as_posix(),
        role=role,
        fingerprint=fingerprint_file(path),
        media_type=media_type,
    )


def _dependency_role(path: Path) -> str:
    if path.suffix.casefold() == ".bin":
        return "buffer"
    return "texture"


def _media_type(path: Path) -> str:
    return {
        ".bin": "application/octet-stream",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.casefold(), "application/octet-stream")

