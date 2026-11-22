# Teaching source map — KairoBlender
**Worked source walkthrough:** [Blender preflight → glTF export → shared publish](https://github.com/swayam8624/KairoPipelineCore/blob/docs/teaching-walkthrough-20261121/docs/CROSS_DCC_PUBLICATION_WALKTHROUGH.md).

Blender artist UX on top of the common Kairo publication contract.

Follow source links sequentially. For each API/function, identify its input contract, owning data structure, called modules, failure modes, outputs, test and downstream consumers.

## Read in this order

1. [`README.md`](../README.md)
2. [`__init__.py`](../__init__.py)
3. [`properties.py`](../properties.py)
4. [`panel.py`](../panel.py)
5. [`operators.py`](../operators.py)
6. [`validation.py`](../validation.py)
7. [`adapter.py`](../adapter.py)
8. [`publisher.py`](../publisher.py)
9. [`scripts`](../scripts)
10. [`tests`](../tests)
11. [`docs`](../docs)

## How this repository interacts with others

Panel/operator code receives user actions; validation identifies issues, adapter translates Blender scene state, publisher writes verifiable artifacts through KairoPipelineCore. Verify Blender versions and permissions.

## Verification and study rules

- Read the public C++23 module/entrypoint first, then its implementation and tests.
- Explain invariants, ownership, error states, concurrency or numerical assumptions in comments, not trivial syntax.
- A passing CI job covers only tests actually run on that commit/host; source presence is not runtime certification.
- Check [STATUS.md](../STATUS.md) and [STATUS.yaml](../STATUS.yaml) for current explicit verification limitations.
- Original work may be modified and extended under the repository license; third-party content retains upstream terms.


## Complete source-file inventory

After the curated teaching path, follow this deterministic inventory of first-party source, scripts, shaders, and tests. Grouping is a suggested learning order, not an indication that every function is already annotated. Vendored dependencies, ROMs, binaries, data, media, and generated evidence are excluded.

### Implementation and other source (8)

1. [`__init__.py`](../__init__.py)
2. [`adapter.py`](../adapter.py)
3. [`examples/create_portfolio_scene.py`](../examples/create_portfolio_scene.py)
4. [`operators.py`](../operators.py)
5. [`panel.py`](../panel.py)
6. [`properties.py`](../properties.py)
7. [`publisher.py`](../publisher.py)
8. [`validation.py`](../validation.py)

### Automation and tooling (1)

1. [`scripts/build_extension.py`](../scripts/build_extension.py)

### Verification and tests (3)

1. [`tests/run_blender_tests.py`](../tests/run_blender_tests.py)
2. [`tests/run_installed_smoke.py`](../tests/run_installed_smoke.py)
3. [`tests/test_validation.py`](../tests/test_validation.py)

Snapshot totals: 12 first-party source/build/test files, 22 tracked files overall. Re-audit when files are renamed or added.
