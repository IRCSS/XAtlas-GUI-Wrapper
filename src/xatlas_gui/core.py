from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import xatlas

from .obj_io import load_obj
from .settings import ChartSettings, PackSettings


@dataclass(frozen=True, slots=True)
class UnwrapResult:
    input_path: Path
    output_path: Path
    input_vertices: int
    input_faces: int
    output_vertices: int
    output_faces: int
    chart_count: int
    atlas_count: int
    width: int
    height: int
    utilization: float | None
    elapsed_seconds: float


def _make_chart_options(settings: ChartSettings) -> xatlas.ChartOptions:
    settings.validate()
    options = xatlas.ChartOptions()
    options.max_chart_area = settings.max_chart_area
    options.max_boundary_length = settings.max_boundary_length
    options.normal_deviation_weight = settings.normal_deviation_weight
    options.roundness_weight = settings.roundness_weight
    options.straightness_weight = settings.straightness_weight
    options.normal_seam_weight = settings.normal_seam_weight
    options.texture_seam_weight = settings.texture_seam_weight
    options.max_cost = settings.max_cost
    options.max_iterations = settings.max_iterations
    options.use_input_mesh_uvs = settings.use_input_mesh_uvs
    options.fix_winding = settings.fix_winding
    return options


def _make_pack_options(settings: PackSettings) -> xatlas.PackOptions:
    settings.validate()
    options = xatlas.PackOptions()
    options.max_chart_size = settings.max_chart_size
    options.padding = settings.padding
    options.texels_per_unit = settings.texels_per_unit
    options.resolution = settings.resolution
    options.bilinear = settings.bilinear
    options.blockAlign = settings.block_align
    options.bruteForce = settings.brute_force
    options.create_image = settings.create_image
    options.rotate_charts_to_axis = settings.rotate_charts_to_axis
    options.rotate_charts = settings.rotate_charts
    return options


def unwrap_obj(
    input_path: Path,
    output_path: Path,
    chart_settings: ChartSettings | None = None,
    pack_settings: PackSettings | None = None,
    *,
    verbose: bool = False,
) -> UnwrapResult:
    """Load, unwrap, pack, and export one OBJ."""
    start = perf_counter()
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()

    if input_path == output_path:
        raise ValueError("Input and output paths must be different")
    if output_path.suffix.lower() != ".obj":
        raise ValueError("Output path must end in .obj")

    vertices, faces = load_obj(input_path)
    chart_settings = chart_settings or ChartSettings()
    pack_settings = pack_settings or PackSettings()

    atlas = xatlas.Atlas()
    atlas.add_mesh(vertices, faces)
    atlas.generate(
        _make_chart_options(chart_settings),
        _make_pack_options(pack_settings),
        verbose,
    )

    vmapping, indices, uvs = atlas[0]
    output_vertices = np.ascontiguousarray(vertices[vmapping], dtype=np.float32)
    output_indices = np.ascontiguousarray(indices, dtype=np.uint32)
    output_uvs = np.ascontiguousarray(uvs, dtype=np.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    xatlas.export(str(output_path), output_vertices, output_indices, output_uvs)

    utilization: float | None
    try:
        utilization = float(atlas.utilization) if atlas.atlas_count else None
    except (RuntimeError, IndexError):
        utilization = None

    return UnwrapResult(
        input_path=input_path,
        output_path=output_path,
        input_vertices=len(vertices),
        input_faces=len(faces),
        output_vertices=len(vmapping),
        output_faces=len(indices),
        chart_count=int(atlas.chart_count),
        atlas_count=int(atlas.atlas_count),
        width=int(atlas.width),
        height=int(atlas.height),
        utilization=utilization,
        elapsed_seconds=perf_counter() - start,
    )
