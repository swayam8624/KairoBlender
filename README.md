# Kairo Blender Bridge

Kairo Blender Bridge is an artist-facing Blender extension for validating and
publishing production assets into the Kairo asset pipeline. It is one part of
the multi-DCC Kairo Production Tools portfolio.

## Current verified host

- Blender 5.2.0 LTS
- Bundled Python 3.13.13
- macOS Apple Silicon

## Native development smoke test

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup \
  --python tests/run_blender_tests.py
```

The initial increment registers an installable extension panel and persistent
scene settings. Validation, export, and publication are delivered in subsequent
small working commits.
