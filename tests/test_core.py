from pathlib import Path

import pytest

from xatlas_gui.core import unwrap_obj
from xatlas_gui.settings import PackSettings


OBJ_TRIANGLE = """\
v 0 0 0
v 1 0 0
v 0 1 0
f 1 2 3
"""


def test_unwrap_obj(tmp_path: Path) -> None:
    source = tmp_path / "triangle.obj"
    output = tmp_path / "triangle_unwrapped.obj"
    source.write_text(OBJ_TRIANGLE, encoding="utf-8")

    result = unwrap_obj(source, output, pack_settings=PackSettings(padding=2, resolution=256))

    assert output.is_file()
    text = output.read_text(encoding="utf-8")
    assert "vt " in text
    assert result.input_faces == 1
    assert result.output_faces == 1


def test_input_and_output_must_differ(tmp_path: Path) -> None:
    source = tmp_path / "triangle.obj"
    source.write_text(OBJ_TRIANGLE, encoding="utf-8")
    with pytest.raises(ValueError, match="different"):
        unwrap_obj(source, source)
