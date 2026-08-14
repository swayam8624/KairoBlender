# Artist Workflow

## 1. Prepare

Save the `.blend` file inside the selected project root. Select the reusable
asset or switch the scope to **Complete Scene**. Enter portable project and
asset identifiers plus an immutable positive version.

## 2. Validate

Choose **Validate for Kairo**. The panel reports errors and warnings with stable
codes. **Select** navigates to the responsible object. Validation covers:

- names and case-insensitive collisions;
- supported static object types;
- hidden render state;
- finite, positive, and applied scale;
- empty or degenerate mesh data;
- primary UV availability;
- Principled material/output availability;
- missing external images; and
- a configurable polygon budget.

Errors block publication. Warnings communicate a production risk but do not
silently alter the asset.

## 3. Apply bounded fixes

**Fix** is offered only for operations with unambiguous intent: portable object
renaming, enabling render visibility, and applying object scale. Topology,
UVs, shaders, and file relinking remain artist-controlled.

All safe fixes are Blender undo operations and validation reruns immediately.

## 4. Plan

**Dry Run** executes validation and the real glTF export in temporary storage,
fingerprints the files, builds the complete publish manifest, and proves the
target can be created. It does not create `Published/` or modify an existing
version.

## 5. Publish

**Publish** exports separate glTF, verifies every file, stages the complete
bundle beside its final destination, and exposes it through one atomic rename.
The panel records the final directory and manifest SHA-256 digest.

Existing versions are protected by default. **Replace Existing Version** must
be chosen explicitly; the old version remains available for rollback until the
new bundle is safely exposed.

## Supported surface

Version 0.1 supports static mesh/empty hierarchies, UVs, normals, tangents, and
Blender's glTF metallic/roughness material export. Animation, arbitrary shader
translation, geometry-node semantics, USD, texture baking, and live sync are
not represented as supported behavior.
