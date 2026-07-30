import pytest

from xatlas_gui.settings import ChartSettings, PackSettings


def test_default_settings_are_valid() -> None:
    ChartSettings().validate()
    PackSettings().validate()


def test_negative_padding_is_rejected() -> None:
    with pytest.raises(ValueError, match="padding"):
        PackSettings(padding=-1).validate()


def test_zero_chart_iterations_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_iterations"):
        ChartSettings(max_iterations=0).validate()
