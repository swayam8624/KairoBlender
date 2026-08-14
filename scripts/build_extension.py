"""Build a reproducible Blender extension package with the pinned core wheel."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


WHEEL_NAME = "kairo_pipeline_core-0.1.0-py3-none-any.whl"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-source", type=Path, required=True)
    parser.add_argument("--blender", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    repository = Path(__file__).resolve().parents[1]
    core = arguments.core_source.resolve(strict=True)
    blender = arguments.blender.resolve(strict=True)
    wheels = repository / "wheels"
    wheels.mkdir(exist_ok=True)
    for stale in wheels.glob("kairo_pipeline_core-*.whl"):
        stale.unlink()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(core),
            "--no-deps",
            "--wheel-dir",
            str(wheels),
        ],
        check=True,
    )
    wheel = wheels / WHEEL_NAME
    if not wheel.is_file():
        raise FileNotFoundError(f"pinned core wheel was not produced: {wheel}")

    output = (
        arguments.output.resolve(strict=False)
        if arguments.output
        else repository / "dist" / "kairo_blender-0.1.0.zip"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(blender),
            "--command",
            "extension",
            "validate",
        ],
        check=True,
        cwd=repository,
    )
    subprocess.run(
        [
            str(blender),
            "--command",
            "extension",
            "build",
            "--source-dir",
            str(repository),
            "--output-filepath",
            str(output),
        ],
        check=True,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
