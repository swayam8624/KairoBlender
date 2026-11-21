# KairoBlender — teaching source reading order

Start with the [README](../README.md), then follow this **workflow-oriented** path. These repositories integrate with [KairoPipelineCore](https://github.com/swayam8624/KairoPipelineCore), the host-neutral Python contracts. The order below describes how a user action reaches validated, publishable data—not the import/build order.

1. [__init__.py](../__init__.py) — read API inputs, output contracts, errors and downstream caller.
2. [properties.py](../properties.py) — read API inputs, output contracts, errors and downstream caller.
3. [panel.py](../panel.py) — read API inputs, output contracts, errors and downstream caller.
4. [adapter.py](../adapter.py) — read API inputs, output contracts, errors and downstream caller.
5. [validation.py](../validation.py) — read API inputs, output contracts, errors and downstream caller.
6. [operators.py](../operators.py) — read API inputs, output contracts, errors and downstream caller.
7. [publisher.py](../publisher.py) — read API inputs, output contracts, errors and downstream caller.
8. [examples/create_portfolio_scene.py](../examples/create_portfolio_scene.py) — read API inputs, output contracts, errors and downstream caller.
9. [scripts/build_extension.py](../scripts/build_extension.py) — read API inputs, output contracts, errors and downstream caller.
10. [tests/test_validation.py](../tests/test_validation.py) — read API inputs, output contracts, errors and downstream caller.
11. [tests/run_blender_tests.py](../tests/run_blender_tests.py) — read API inputs, output contracts, errors and downstream caller.
12. [tests/run_installed_smoke.py](../tests/run_installed_smoke.py) — read API inputs, output contracts, errors and downstream caller.

## Data flow

Blender UI panel/operators → bpy scene/datablock snapshot (adapter.py) → immutable validation snapshots/rules (validation.py) → user-visible diagnostics and permitted fixes → glTF export plus file fingerprinting (publisher.py) → shared KairoPipelineCore manifest/plan_publish/publish_bundle. The host-specific bpy module must not leak into portable validation tests.

## Boundary of the tests

Host-neutral tests cover validation only. Blender's native UI/extension install, exporters and background tests require the documented Blender host and version; they cannot be certified by standard Python mocks.

## Teaching exercises

1. Trace one host action or command into a pure validation function and its structured diagnostic.
2. Identify where filesystem paths are normalized and hashed before publishing.
3. Feed malformed/missing files to the host-neutral path and locate the specific failure/diagnostic.
4. Run the portable tests; then read the native verification checklist before claiming host support.
5. Explain why a dry-run plan, a completed atomic publish, and a native host import are three different events.

## Licensing

Preserve the repository's existing [LICENSE](../LICENSE). The original source and documentation permit learning and development according to that file; external DCC SDKs, plugins, images and example assets retain their own terms.
