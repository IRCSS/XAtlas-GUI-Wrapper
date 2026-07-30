from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .cli import format_result
from .core import UnwrapResult, unwrap_obj
from .settings import ChartSettings, PackSettings


class UnwrapWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        chart_settings: ChartSettings,
        pack_settings: PackSettings,
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.chart_settings = chart_settings
        self.pack_settings = pack_settings

    @Slot()
    def run(self) -> None:
        try:
            result = unwrap_obj(
                self.input_path,
                self.output_path,
                self.chart_settings,
                self.pack_settings,
            )
            self.succeeded.emit(result)
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("XAtlas OBJ Unwrapper")
        self.resize(760, 720)
        self._thread: QThread | None = None
        self._worker: UnwrapWorker | None = None
        self._settings = QSettings("Realities.io", "XAtlasGUI")

        central = QWidget(self)
        root = QVBoxLayout(central)
        self.setCentralWidget(central)

        files = QGroupBox("Files")
        file_grid = QGridLayout(files)
        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit()
        input_browse = QPushButton("Browse…")
        output_browse = QPushButton("Browse…")
        input_browse.clicked.connect(self._browse_input)
        output_browse.clicked.connect(self._browse_output)
        file_grid.addWidget(QLabel("Input OBJ"), 0, 0)
        file_grid.addWidget(self.input_edit, 0, 1)
        file_grid.addWidget(input_browse, 0, 2)
        file_grid.addWidget(QLabel("Output OBJ"), 1, 0)
        file_grid.addWidget(self.output_edit, 1, 1)
        file_grid.addWidget(output_browse, 1, 2)
        root.addWidget(files)

        tabs = QTabWidget()
        tabs.addTab(self._build_chart_tab(), "Unwrap / Charts")
        tabs.addTab(self._build_pack_tab(), "Packing")
        root.addWidget(tabs)

        action_row = QHBoxLayout()
        self.reset_button = QPushButton("Reset defaults")
        self.unwrap_button = QPushButton("Unwrap OBJ")
        self.unwrap_button.setDefault(True)
        self.reset_button.clicked.connect(self._reset_defaults)
        self.unwrap_button.clicked.connect(self._start_unwrap)
        action_row.addWidget(self.reset_button)
        action_row.addStretch(1)
        action_row.addWidget(self.unwrap_button)
        root.addLayout(action_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        root.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Results and errors appear here.")
        root.addWidget(self.log, 1)

        self._restore_paths()

    def _double_spin(self, value: float, maximum: float = 1_000_000.0) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setDecimals(4)
        box.setRange(0.0, maximum)
        box.setValue(value)
        box.setSingleStep(0.1)
        return box

    def _int_spin(self, value: int, maximum: int = 1_000_000) -> QSpinBox:
        box = QSpinBox()
        box.setRange(0, maximum)
        box.setValue(value)
        return box

    def _build_chart_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        defaults = ChartSettings()
        self.max_chart_area = self._double_spin(defaults.max_chart_area)
        self.max_boundary_length = self._double_spin(defaults.max_boundary_length)
        self.normal_deviation_weight = self._double_spin(defaults.normal_deviation_weight)
        self.roundness_weight = self._double_spin(defaults.roundness_weight)
        self.straightness_weight = self._double_spin(defaults.straightness_weight)
        self.normal_seam_weight = self._double_spin(defaults.normal_seam_weight)
        self.texture_seam_weight = self._double_spin(defaults.texture_seam_weight)
        self.max_cost = self._double_spin(defaults.max_cost)
        self.max_iterations = self._int_spin(defaults.max_iterations, 100)
        self.max_iterations.setMinimum(1)
        self.use_input_mesh_uvs = QCheckBox()
        self.fix_winding = QCheckBox()

        form.addRow("Max chart area (0 = unlimited)", self.max_chart_area)
        form.addRow("Max boundary length (0 = unlimited)", self.max_boundary_length)
        form.addRow("Normal deviation weight", self.normal_deviation_weight)
        form.addRow("Roundness weight", self.roundness_weight)
        form.addRow("Straightness weight", self.straightness_weight)
        form.addRow("Normal seam weight", self.normal_seam_weight)
        form.addRow("Texture seam weight", self.texture_seam_weight)
        form.addRow("Max chart-growth cost", self.max_cost)
        form.addRow("Chart iterations", self.max_iterations)
        form.addRow("Use input mesh UVs", self.use_input_mesh_uvs)
        form.addRow("Fix UV winding", self.fix_winding)
        return tab

    def _build_pack_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        defaults = PackSettings()
        self.max_chart_size = self._int_spin(defaults.max_chart_size)
        self.padding = self._int_spin(defaults.padding, 4096)
        self.texels_per_unit = self._double_spin(defaults.texels_per_unit)
        self.resolution = self._int_spin(defaults.resolution, 65536)
        self.bilinear = QCheckBox()
        self.bilinear.setChecked(defaults.bilinear)
        self.block_align = QCheckBox()
        self.brute_force = QCheckBox()
        self.create_image = QCheckBox()
        self.rotate_charts_to_axis = QCheckBox()
        self.rotate_charts_to_axis.setChecked(defaults.rotate_charts_to_axis)
        self.rotate_charts = QCheckBox()
        self.rotate_charts.setChecked(defaults.rotate_charts)

        form.addRow("Max chart size (pixels; 0 = unlimited)", self.max_chart_size)
        form.addRow("Padding (pixels)", self.padding)
        form.addRow("Texels per unit (0 = estimate)", self.texels_per_unit)
        form.addRow("Resolution (0 = automatic)", self.resolution)
        form.addRow("Bilinear padding", self.bilinear)
        form.addRow("Align to 4×4 blocks", self.block_align)
        form.addRow("Brute-force packing", self.brute_force)
        form.addRow("Create debug chart image", self.create_image)
        form.addRow("Rotate charts to axis", self.rotate_charts_to_axis)
        form.addRow("Rotate charts for packing", self.rotate_charts)
        return tab

    @Slot()
    def _browse_input(self) -> None:
        start = self.input_edit.text() or str(Path.home())
        filename, _ = QFileDialog.getOpenFileName(self, "Choose OBJ", start, "Wavefront OBJ (*.obj)")
        if not filename:
            return
        path = Path(filename)
        self.input_edit.setText(str(path))
        if not self.output_edit.text():
            self.output_edit.setText(str(path.with_name(f"{path.stem}_unwrapped.obj")))

    @Slot()
    def _browse_output(self) -> None:
        start = self.output_edit.text() or self.input_edit.text() or str(Path.home())
        filename, _ = QFileDialog.getSaveFileName(self, "Save unwrapped OBJ", start, "Wavefront OBJ (*.obj)")
        if filename:
            path = Path(filename)
            if path.suffix.lower() != ".obj":
                path = path.with_suffix(".obj")
            self.output_edit.setText(str(path))

    def _chart_settings(self) -> ChartSettings:
        return ChartSettings(
            max_chart_area=self.max_chart_area.value(),
            max_boundary_length=self.max_boundary_length.value(),
            normal_deviation_weight=self.normal_deviation_weight.value(),
            roundness_weight=self.roundness_weight.value(),
            straightness_weight=self.straightness_weight.value(),
            normal_seam_weight=self.normal_seam_weight.value(),
            texture_seam_weight=self.texture_seam_weight.value(),
            max_cost=self.max_cost.value(),
            max_iterations=self.max_iterations.value(),
            use_input_mesh_uvs=self.use_input_mesh_uvs.isChecked(),
            fix_winding=self.fix_winding.isChecked(),
        )

    def _pack_settings(self) -> PackSettings:
        return PackSettings(
            max_chart_size=self.max_chart_size.value(),
            padding=self.padding.value(),
            texels_per_unit=self.texels_per_unit.value(),
            resolution=self.resolution.value(),
            bilinear=self.bilinear.isChecked(),
            block_align=self.block_align.isChecked(),
            brute_force=self.brute_force.isChecked(),
            create_image=self.create_image.isChecked(),
            rotate_charts_to_axis=self.rotate_charts_to_axis.isChecked(),
            rotate_charts=self.rotate_charts.isChecked(),
        )

    @Slot()
    def _start_unwrap(self) -> None:
        try:
            input_path = Path(self.input_edit.text().strip())
            output_path = Path(self.output_edit.text().strip())
            if not self.input_edit.text().strip() or not self.output_edit.text().strip():
                raise ValueError("Choose both an input and output OBJ")
            chart_settings = self._chart_settings()
            pack_settings = self._pack_settings()
            chart_settings.validate()
            pack_settings.validate()
        except Exception as exc:
            QMessageBox.warning(self, "Invalid settings", str(exc))
            return

        self._settings.setValue("last_input", str(input_path))
        self._settings.setValue("last_output", str(output_path))
        self._set_busy(True)
        self.log.setPlainText("Unwrapping…")

        self._thread = QThread(self)
        self._worker = UnwrapWorker(input_path, output_path, chart_settings, pack_settings)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.succeeded.connect(self._unwrap_succeeded)
        self._worker.failed.connect(self._unwrap_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._thread_finished)
        self._thread.start()

    @Slot(object)
    def _unwrap_succeeded(self, result: UnwrapResult) -> None:
        self.log.setPlainText(format_result(result))
        QMessageBox.information(self, "Finished", f"Unwrapped OBJ written to:\n{result.output_path}")

    @Slot(str)
    def _unwrap_failed(self, details: str) -> None:
        self.log.setPlainText(details)
        QMessageBox.critical(self, "Unwrap failed", details.splitlines()[-1] if details else "Unknown error")

    @Slot()
    def _thread_finished(self) -> None:
        self._worker = None
        self._thread = None
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self.unwrap_button.setEnabled(not busy)
        self.reset_button.setEnabled(not busy)
        self.progress.setRange(0, 0 if busy else 1)
        if not busy:
            self.progress.setValue(1)

    @Slot()
    def _reset_defaults(self) -> None:
        chart = ChartSettings()
        pack = PackSettings()
        self.max_chart_area.setValue(chart.max_chart_area)
        self.max_boundary_length.setValue(chart.max_boundary_length)
        self.normal_deviation_weight.setValue(chart.normal_deviation_weight)
        self.roundness_weight.setValue(chart.roundness_weight)
        self.straightness_weight.setValue(chart.straightness_weight)
        self.normal_seam_weight.setValue(chart.normal_seam_weight)
        self.texture_seam_weight.setValue(chart.texture_seam_weight)
        self.max_cost.setValue(chart.max_cost)
        self.max_iterations.setValue(chart.max_iterations)
        self.use_input_mesh_uvs.setChecked(chart.use_input_mesh_uvs)
        self.fix_winding.setChecked(chart.fix_winding)
        self.max_chart_size.setValue(pack.max_chart_size)
        self.padding.setValue(pack.padding)
        self.texels_per_unit.setValue(pack.texels_per_unit)
        self.resolution.setValue(pack.resolution)
        self.bilinear.setChecked(pack.bilinear)
        self.block_align.setChecked(pack.block_align)
        self.brute_force.setChecked(pack.brute_force)
        self.create_image.setChecked(pack.create_image)
        self.rotate_charts_to_axis.setChecked(pack.rotate_charts_to_axis)
        self.rotate_charts.setChecked(pack.rotate_charts)

    def _restore_paths(self) -> None:
        self.input_edit.setText(str(self._settings.value("last_input", "")))
        self.output_edit.setText(str(self._settings.value("last_output", "")))


def run_gui(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    app.setApplicationName("XAtlas GUI")
    app.setOrganizationName("Realities.io")
    window = MainWindow()
    window.show()
    return app.exec()
