from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChartSettings:
    max_chart_area: float = 0.0
    max_boundary_length: float = 0.0
    normal_deviation_weight: float = 2.0
    roundness_weight: float = 0.01
    straightness_weight: float = 6.0
    normal_seam_weight: float = 4.0
    texture_seam_weight: float = 0.5
    max_cost: float = 2.0
    max_iterations: int = 1
    use_input_mesh_uvs: bool = False
    fix_winding: bool = False

    def validate(self) -> None:
        non_negative = {
            "max_chart_area": self.max_chart_area,
            "max_boundary_length": self.max_boundary_length,
            "normal_deviation_weight": self.normal_deviation_weight,
            "roundness_weight": self.roundness_weight,
            "straightness_weight": self.straightness_weight,
            "normal_seam_weight": self.normal_seam_weight,
            "texture_seam_weight": self.texture_seam_weight,
            "max_cost": self.max_cost,
        }
        for name, value in non_negative.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")


@dataclass(slots=True)
class PackSettings:
    max_chart_size: int = 0
    padding: int = 0
    texels_per_unit: float = 0.0
    resolution: int = 0
    bilinear: bool = True
    block_align: bool = False
    brute_force: bool = False
    create_image: bool = False
    rotate_charts_to_axis: bool = True
    rotate_charts: bool = True

    def validate(self) -> None:
        if self.max_chart_size < 0:
            raise ValueError("max_chart_size must be non-negative")
        if self.padding < 0:
            raise ValueError("padding must be non-negative")
        if self.texels_per_unit < 0:
            raise ValueError("texels_per_unit must be non-negative")
        if self.resolution < 0:
            raise ValueError("resolution must be non-negative")
