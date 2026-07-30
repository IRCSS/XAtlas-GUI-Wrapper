from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh


class ObjLoadError(RuntimeError):
    pass


def load_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load an OBJ as one triangle mesh, flattening a Scene when necessary."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Input OBJ does not exist: {path}")
    if path.suffix.lower() != ".obj":
        raise ObjLoadError(f"Expected an .obj file, got: {path.name}")

    try:
        loaded = trimesh.load(path, process=False, force=None)
    except Exception as exc:
        raise ObjLoadError(f"Could not load OBJ '{path}': {exc}") from exc

    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ObjLoadError("The OBJ scene contains no triangle meshes")
        mesh = trimesh.util.concatenate(meshes)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise ObjLoadError(f"Unsupported OBJ result type: {type(loaded).__name__}")

    if len(mesh.vertices) == 0:
        raise ObjLoadError("The OBJ contains no vertices")
    if len(mesh.faces) == 0:
        raise ObjLoadError("The OBJ contains no faces")
    if mesh.faces.ndim != 2 or mesh.faces.shape[1] != 3:
        raise ObjLoadError("The OBJ must contain triangulated faces")

    vertices = np.ascontiguousarray(mesh.vertices, dtype=np.float32)
    faces = np.ascontiguousarray(mesh.faces, dtype=np.uint32)
    return vertices, faces
