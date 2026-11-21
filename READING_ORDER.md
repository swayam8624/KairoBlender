# KairoBlender — source reading path and API interactions

Start with the Blender extension registration/panel/property data, then validation and artist-facing operators, glTF adapter, publish handoff and native Blender smoke tests. Unlike generic Python scripts, Blender bpy APIs require a running Blender host; pure validator tests cannot prove the UI integration works.

## Key interfaces and cross-repository calls

bpy registration and operators modify artist-owned scene data under explicit requests; KairoPipelineCore manifests and atomic publish preserve provenance. Compare dry-run versus actual mutation and keep source .blend unmodified on failure.

## Read the source and tests in this order (12 files)

1. [`__init__.py`](__init__.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
2. [`properties.py`](properties.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
3. [`validation.py`](validation.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
4. [`operators.py`](operators.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
5. [`panel.py`](panel.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
6. [`adapter.py`](adapter.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
7. [`publisher.py`](publisher.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
8. [`tests/test_validation.py`](tests/test_validation.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
9. [`tests/run_blender_tests.py`](tests/run_blender_tests.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
10. [`tests/run_installed_smoke.py`](tests/run_installed_smoke.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
11. [`examples/create_portfolio_scene.py`](examples/create_portfolio_scene.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.
12. [`scripts/build_extension.py`](scripts/build_extension.py) — inspect its callers and imports, owned resources, validated inputs, failure states, and matching tests.

## Licensing and verification

This repository already has its own [LICENSE](LICENSE). Blender bridge code retains **GPL-3.0-or-later** terms; do not replace them with the MIT license in sibling repositories. Native DCC app APIs and third-party assets retain their own conditions. Read [README](README.md) for host-specific setup; pure tests cannot establish all native integration gates. Further in-file function annotations will complement this guide.
