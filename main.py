from __future__ import annotations

import sys

import numpy as np
import xatlas


def main() -> int:
    vertices = np.array(
        [
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ],
        dtype=np.uint32,
    )

    vmapping, indices, uvs = xatlas.parametrize(vertices, faces)

    print("xatlas imported successfully")
    print(f"Python: {sys.version}")
    print(f"Input vertices: {len(vertices)}")
    print(f"Output vertices: {len(vmapping)}")
    print(f"Output triangles: {len(indices)}")
    print(f"UV array shape: {uvs.shape}")
    print("UV coordinates:")
    print(uvs)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())