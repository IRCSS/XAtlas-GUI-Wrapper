from __future__ import annotations

import argparse
from pathlib import Path

import trimesh
import xatlas


def unwrap_obj(input_path: Path, output_path: Path) -> None:
    loaded = trimesh.load(input_path, force="mesh", process=False)

    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"Expected one mesh, received {type(loaded).__name__}")

    if len(loaded.vertices) == 0 or len(loaded.faces) == 0:
        raise ValueError("The OBJ contains no usable triangle mesh.")

    vmapping, indices, uvs = xatlas.parametrize(
        loaded.vertices,
        loaded.faces,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    xatlas.export(
        str(output_path),
        loaded.vertices[vmapping],
        indices,
        uvs,
    )

    print(f"Input:  {input_path.resolve()}")
    print(f"Output: {output_path.resolve()}")
    print(f"Atlas vertices: {len(vmapping)}")
    print(f"Atlas triangles: {len(indices)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic xatlas OBJ test")
    parser.add_argument("input", type=Path, help="Input OBJ path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("unwrapped.obj"),
        help="Output OBJ path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(args.input)

    unwrap_obj(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())