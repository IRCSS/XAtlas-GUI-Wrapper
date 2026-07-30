from __future__ import annotations

import argparse
from pathlib import Path

from .core import UnwrapResult, unwrap_obj
from .settings import ChartSettings, PackSettings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xatlas-gui",
        description="Unwrap and pack an OBJ using the xatlas Python binding.",
    )
    parser.add_argument("--input", "-i", type=Path, help="Input OBJ. Supplying this enables CLI mode.")
    parser.add_argument("--output", "-o", type=Path, help="Output OBJ path")
    parser.add_argument("--silent", action="store_true", help="Suppress normal CLI output")
    parser.add_argument("--verbose-xatlas", action="store_true", help="Enable native xatlas logging")

    chart = parser.add_argument_group("chart generation")
    chart.add_argument("--max-chart-area", type=float, default=0.0)
    chart.add_argument("--max-boundary-length", type=float, default=0.0)
    chart.add_argument("--normal-deviation-weight", type=float, default=2.0)
    chart.add_argument("--roundness-weight", type=float, default=0.01)
    chart.add_argument("--straightness-weight", type=float, default=6.0)
    chart.add_argument("--normal-seam-weight", type=float, default=4.0)
    chart.add_argument("--texture-seam-weight", type=float, default=0.5)
    chart.add_argument("--max-cost", type=float, default=2.0)
    chart.add_argument("--max-iterations", type=int, default=1)
    chart.add_argument("--use-input-mesh-uvs", action=argparse.BooleanOptionalAction, default=False)
    chart.add_argument("--fix-winding", action=argparse.BooleanOptionalAction, default=False)

    pack = parser.add_argument_group("packing")
    pack.add_argument("--max-chart-size", type=int, default=0)
    pack.add_argument("--padding", type=int, default=0)
    pack.add_argument("--texels-per-unit", type=float, default=0.0)
    pack.add_argument("--resolution", type=int, default=0)
    pack.add_argument("--bilinear", action=argparse.BooleanOptionalAction, default=True)
    pack.add_argument("--block-align", action=argparse.BooleanOptionalAction, default=False)
    pack.add_argument("--brute-force", action=argparse.BooleanOptionalAction, default=False)
    pack.add_argument("--create-image", action=argparse.BooleanOptionalAction, default=False)
    pack.add_argument("--rotate-charts-to-axis", action=argparse.BooleanOptionalAction, default=True)
    pack.add_argument("--rotate-charts", action=argparse.BooleanOptionalAction, default=True)
    return parser


def _settings_from_args(args: argparse.Namespace) -> tuple[ChartSettings, PackSettings]:
    return (
        ChartSettings(
            max_chart_area=args.max_chart_area,
            max_boundary_length=args.max_boundary_length,
            normal_deviation_weight=args.normal_deviation_weight,
            roundness_weight=args.roundness_weight,
            straightness_weight=args.straightness_weight,
            normal_seam_weight=args.normal_seam_weight,
            texture_seam_weight=args.texture_seam_weight,
            max_cost=args.max_cost,
            max_iterations=args.max_iterations,
            use_input_mesh_uvs=args.use_input_mesh_uvs,
            fix_winding=args.fix_winding,
        ),
        PackSettings(
            max_chart_size=args.max_chart_size,
            padding=args.padding,
            texels_per_unit=args.texels_per_unit,
            resolution=args.resolution,
            bilinear=args.bilinear,
            block_align=args.block_align,
            brute_force=args.brute_force,
            create_image=args.create_image,
            rotate_charts_to_axis=args.rotate_charts_to_axis,
            rotate_charts=args.rotate_charts,
        ),
    )


def _default_output(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_unwrapped.obj")


def format_result(result: UnwrapResult) -> str:
    utilization = "n/a" if result.utilization is None else f"{result.utilization:.1%}"
    return (
        f"Wrote: {result.output_path}\n"
        f"Input: {result.input_vertices:,} vertices, {result.input_faces:,} faces\n"
        f"Output: {result.output_vertices:,} vertices, {result.output_faces:,} faces\n"
        f"Charts: {result.chart_count:,}; atlas: {result.width}x{result.height}; utilization: {utilization}\n"
        f"Elapsed: {result.elapsed_seconds:.2f}s"
    )


def run_cli(args: argparse.Namespace) -> int:
    if args.input is None:
        raise ValueError("--input is required in CLI mode")
    output = args.output or _default_output(args.input)
    chart_settings, pack_settings = _settings_from_args(args)
    result = unwrap_obj(
        args.input,
        output,
        chart_settings,
        pack_settings,
        verbose=args.verbose_xatlas,
    )
    if not args.silent:
        print(format_result(result))
    return 0
