# KairoBlender Status

Wave: A — native production-tool certification  
Frozen v1 target: 95/100  
Source gate: complete  
Native gate: Blender 5.2 LTS headless suite

## Frozen v1 scope

KairoBlender v1 validates static publishable assets, navigates diagnostics, applies only bounded safe fixes, exports separate glTF, fingerprints all payloads, supports non-mutating dry-run, and atomically publishes through KairoPipelineCore. Full Blender replacement, rigging tools and arbitrary artistic repair are out of scope.

## 95 exit evidence

- Native extension registration/unregistration is tested.
- Native diagnostic navigation and safe transform repair are tested.
- Real Blender glTF export, dry-run and atomic publication are tested.
- Publication now rejects unsaved Blender state so the source fingerprint cannot describe a different file than the scene that was exported.
- Certification tests cover immutable existing versions, explicit replacement, dirty-scene rejection and saved replacement provenance.

## Verification policy

The source is ready for 95 certification. The exact release SHA is considered natively verified only after:

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup \
  --python tests/run_blender_tests.py
```
