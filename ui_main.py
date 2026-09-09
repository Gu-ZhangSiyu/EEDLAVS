import os
import sys
import traceback
import io
import webbrowser
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
import imageka
import gifka
import waveka
import datahandle
import Particlestrajectory
import Pandtgif
import run_DebugError
from config import Config


class LogoTextEdit(QtWidgets.QTextEdit):
    def __init__(self, logo_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo = QtGui.QPixmap(logo_path)
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self.viewport())
        w, h = self.viewport().width(), self.viewport().height()
        lw, lh = self.logo.width(), self.logo.height()
        x = (w - lw) // 2
        y = (h - lh) // 2
        painter.drawPixmap(x, y, self.logo)

        # Author credit.
        text = "Author: SIYU ZHANG"
        font = painter.font()
        font.setPointSize(8)        # Font size.
        painter.setFont(font)
        fm = QtGui.QFontMetrics(font)
        tw = fm.horizontalAdvance(text)
        th = fm.height()
        margin = 4                  # Margin.
        x_text = w - tw - margin
        y_text = h - margin         # Leave a small margin at the bottom.
        painter.drawText(x_text, y_text, text)
        painter.end()

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))
    def flush(self):
        pass

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("EEDLAVS")
        self.resize(800, 800)       # Window size.

        # Central widget and main layout.
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        # Log output box using a custom widget with a logo.
        if getattr(sys, '_MEIPASS', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, 'sw_logo.png')  # Software icon logo.
        self.setWindowIcon(QtGui.QIcon(icon_path))
        logo_path = os.path.join(base_path, 'lab_logo.png') # Output-box background.
        self.text_output = LogoTextEdit(logo_path, self)
        self.text_output.setReadOnly(True)
        main_layout.addWidget(self.text_output)
        self.text_output.setMaximumHeight(300)  # Maximum height in pixels.

        # Redirect stdout and stderr to the log box.
        sys.stdout = EmittingStream()
        sys.stdout.textWritten.connect(self._append_output)
        sys.stderr = EmittingStream()
        sys.stderr.textWritten.connect(self._append_output)

        # Parameter area (three columns).
        param_container = QtWidgets.QWidget(self)
        param_layout = QtWidgets.QHBoxLayout(param_container)

        # Feature list.
        func_group = QtWidgets.QGroupBox("Feature list (only the first selected feature is enabled)", self)
        func_layout = QtWidgets.QVBoxLayout(func_group)
        # Data analysis.
        self.cb_handle = QtWidgets.QCheckBox("Data Handle", self)
        self.cb_handle.setChecked(self.cfg.data_handle)
        self.cb_handle.stateChanged.connect(lambda st: setattr(self.cfg, "data_handle", int(bool(st))))
        func_layout.addWidget(self.cb_handle)
        # 2D Image
        self.cb_2d = QtWidgets.QCheckBox("2D Image", self)
        self.cb_2d.setChecked(self.cfg.dimension_2D)
        self.cb_2d.stateChanged.connect(lambda st: setattr(self.cfg, "dimension_2D", int(bool(st))))
        func_layout.addWidget(self.cb_2d)
        # 2D GIF
        self.cb_gif2d = QtWidgets.QCheckBox("2D GIF", self)
        self.cb_gif2d.setChecked(self.cfg.GIF_2D)
        self.cb_gif2d.stateChanged.connect(lambda st: setattr(self.cfg, "GIF_2D", int(bool(st))))
        func_layout.addWidget(self.cb_gif2d)
        # Array-extraction line chart.
        self.cb_single_line = QtWidgets.QCheckBox("Array-extraction line chart", self)
        self.cb_single_line.setChecked(self.cfg.single_array_line)
        self.cb_single_line.stateChanged.connect(lambda st: setattr(self.cfg, "single_array_line", int(bool(st))))
        func_layout.addWidget(self.cb_single_line)
        # Selected-point data evolution.
        self.cb_point_selection = QtWidgets.QCheckBox("Selected-point data evolution", self)
        self.cb_point_selection.setChecked(self.cfg.point_Selection)
        self.cb_point_selection.stateChanged.connect(lambda st: setattr(self.cfg, "point_Selection", int(bool(st))))
        func_layout.addWidget(self.cb_point_selection)
        # Particle trajectories and scatter plot.
        self.cb_part_traj = QtWidgets.QCheckBox("Particle trajectories/scatter plot", self)
        self.cb_part_traj.setChecked(self.cfg.part_traj)
        self.cb_part_traj.stateChanged.connect(lambda st: setattr(self.cfg, "part_traj", int(bool(st))))
        func_layout.addWidget(self.cb_part_traj)
        # Particle trajectories and scatter GIF.
        self.cb_part_traj_gif = QtWidgets.QCheckBox("Particle trajectories/scatter GIF", self)
        self.cb_part_traj_gif.setChecked(self.cfg.part_traj_gif)
        self.cb_part_traj_gif.stateChanged.connect(lambda st: setattr(self.cfg, "part_traj_gif", int(bool(st))))
        func_layout.addWidget(self.cb_part_traj_gif)
        # Open TarGo in an external browser.
        self.btn_targo = QtWidgets.QPushButton("link to TarGo", self)
        self.btn_targo.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_targo.setStyleSheet("""
            QPushButton {
                color: #0066ff;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
                padding: 4px 10px;
                border: 1px solid #0066ff;
                border-radius: 4px;
                background: #eef5ff;
            }
            QPushButton:hover {
                color: #00aaff;
                text-decoration: underline;
                background: #dcecff;
            }
            QPushButton:pressed {
                background: #c6ddff;
            }
        """)
        self.btn_targo.clicked.connect(self.open_targo)
        param_layout.addWidget(func_group)      # Add the feature-list area to the main layout.

        # General parameters.
        common_group = QtWidgets.QGroupBox("General parameters", self)
        common_layout = QtWidgets.QFormLayout(common_group)
        # Input file path display.
        self.le_input_path = QtWidgets.QLineEdit(self.cfg.input_path, self)
        self.le_input_path.setReadOnly(True)
        self.le_input_path.mousePressEvent = self._on_input_path_click  # Override the mouse-click event.
        common_layout.addRow("Input file path:", self.le_input_path)
        # Input folder path display.
        self.le_file_path = QtWidgets.QLineEdit(self.cfg.file_path, self)
        self.le_file_path.setReadOnly(True)
        self.le_file_path.mousePressEvent = self._on_file_path_click
        common_layout.addRow("Input folder path:", self.le_file_path)
        self.le_output_path = QtWidgets.QLineEdit(self.cfg.output_path, self)
        self.le_output_path.setReadOnly(True)
        self.le_output_path.mousePressEvent = self._on_output_path_click
        common_layout.addRow("Output folder path:", self.le_output_path)
        # Scale system (boolean/enum).
        self.cb_grid_ratio = QtWidgets.QComboBox(self)
        self.cb_grid_ratio.addItems(["Grid scale", "Device scale"])
        self.cb_grid_ratio.setCurrentIndex(self.cfg.Grid_Ratio)
        self.cb_grid_ratio.currentIndexChanged.connect(lambda idx: setattr(self.cfg, "Grid_Ratio", idx))
        common_layout.addRow("Scale system:", self.cb_grid_ratio)
        # Device radius physical_R.
        self.cb_physical_R = QtWidgets.QDoubleSpinBox(self)
        self.cb_physical_R.setRange(0.0, 10.0)  # Adjust according to the physical range.
        self.cb_physical_R.setDecimals(4)  # Keep four decimal places.
        self.cb_physical_R.setSingleStep(0.0001)  # Single-step increment.
        self.cb_physical_R.setValue(self.cfg.physical_R)
        self.cb_physical_R.valueChanged.connect(lambda val: setattr(self.cfg, "physical_R", val))
        common_layout.addRow("Device radius (m):", self.cb_physical_R)
        # Device axial length physical_Z.
        self.cb_physical_Z = QtWidgets.QDoubleSpinBox(self)
        self.cb_physical_Z.setRange(0.0, 10.0)
        self.cb_physical_Z.setDecimals(4)
        self.cb_physical_Z.setSingleStep(0.0001)
        self.cb_physical_Z.setValue(self.cfg.physical_Z)
        self.cb_physical_Z.valueChanged.connect(lambda val: setattr(self.cfg, "physical_Z", val))
        common_layout.addRow("Device length (m):", self.cb_physical_Z)
        # Cylindrical grid dimension NR.
        self.sb_NR = QtWidgets.QSpinBox(self)
        self.sb_NR.setRange(1, 1000)
        self.sb_NR.setValue(self.cfg.NR)
        self.sb_NR.valueChanged.connect(lambda val: setattr(self.cfg, "NR", val))
        common_layout.addRow("NR (cylindrical coordinates):", self.sb_NR)
        # Cylindrical grid dimension Nth.
        self.sb_Nth = QtWidgets.QSpinBox(self)
        self.sb_Nth.setRange(1, 1000)
        self.sb_Nth.setValue(self.cfg.nth)
        self.sb_Nth.valueChanged.connect(lambda val: setattr(self.cfg, "nth", val))
        common_layout.addRow("Nth:", self.sb_Nth)
        # Cylindrical grid dimension nz.
        self.sb_nz = QtWidgets.QSpinBox(self)
        self.sb_nz.setRange(1, 1000)
        self.sb_nz.setValue(self.cfg.nz)
        self.sb_nz.valueChanged.connect(lambda val: setattr(self.cfg, "nz", val))
        common_layout.addRow("NZ:", self.sb_nz)
        param_layout.addWidget(common_group)        # Add the global-parameter area to the main layout.

        # Data-analysis-specific parameters.
        self.param_handle_group = QtWidgets.QGroupBox("Data-analysis-specific parameters", self)
        param_handle_layout = QtWidgets.QVBoxLayout(self.param_handle_group)
        param_handle_layout.addWidget(
            QtWidgets.QLabel("The following features use the input file path from the general parameters above"))
        # Discrete analysis (boolean).
        self.cb_lsf = QtWidgets.QCheckBox("Discrete analysis", self)
        self.cb_lsf.setChecked(self.cfg.data_discrete)
        self.cb_lsf.stateChanged.connect(lambda st: setattr(self.cfg, "data_discrete", int(bool(st))))
        param_handle_layout.addWidget(self.cb_lsf)
        # Single-file extrema (boolean).
        self.cb_djz = QtWidgets.QCheckBox("Single-file extrema", self)
        self.cb_djz.setChecked(self.cfg.file_extreme)
        self.cb_djz.stateChanged.connect(lambda st: setattr(self.cfg, "file_extreme", int(bool(st))))
        param_handle_layout.addWidget(self.cb_djz)

        # 3D field dimensionality reduction (3D bin to 2D txt).
        self.cb_dh_slice = QtWidgets.QCheckBox("3D field dimensionality reduction (3D bin to 2D txt)", self)
        self.cb_dh_slice.setChecked(self.cfg.data_3d_to_2d)
        self.cb_dh_slice.stateChanged.connect(lambda st: setattr(self.cfg, "data_3d_to_2d", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_slice)
        self.dh_slice_params = QtWidgets.QWidget(self)
        dh_slice_layout = QtWidgets.QFormLayout(self.dh_slice_params)
        slice_grid_layout = QtWidgets.QHBoxLayout()
        self.sb_data_3d_nx = QtWidgets.QSpinBox(self)
        self.sb_data_3d_nx.setRange(1, 100000)
        self.sb_data_3d_nx.setValue(self.cfg.data_3d_nx)
        self.sb_data_3d_nx.valueChanged.connect(lambda v: setattr(self.cfg, "data_3d_nx", v))
        self.sb_data_3d_ny = QtWidgets.QSpinBox(self)
        self.sb_data_3d_ny.setRange(1, 100000)
        self.sb_data_3d_ny.setValue(self.cfg.data_3d_ny)
        self.sb_data_3d_ny.valueChanged.connect(lambda v: setattr(self.cfg, "data_3d_ny", v))
        self.sb_data_3d_nz = QtWidgets.QSpinBox(self)
        self.sb_data_3d_nz.setRange(1, 100000)
        self.sb_data_3d_nz.setValue(self.cfg.data_3d_nz)
        self.sb_data_3d_nz.valueChanged.connect(lambda v: setattr(self.cfg, "data_3d_nz", v))
        slice_grid_layout.addWidget(QtWidgets.QLabel("NX:"))
        slice_grid_layout.addWidget(self.sb_data_3d_nx)
        slice_grid_layout.addWidget(QtWidgets.QLabel("NY:"))
        slice_grid_layout.addWidget(self.sb_data_3d_ny)
        slice_grid_layout.addWidget(QtWidgets.QLabel("NZ:"))
        slice_grid_layout.addWidget(self.sb_data_3d_nz)
        dh_slice_layout.addRow("Original .bin file structure:", slice_grid_layout)
        slice_mode_layout = QtWidgets.QHBoxLayout()
        self.cb_data_3d_plane = QtWidgets.QComboBox(self)
        self.cb_data_3d_plane.addItems(["XZ", "XY"])
        self.cb_data_3d_plane.setCurrentText(self.cfg.data_3d_plane)
        self.cb_data_3d_plane.currentTextChanged.connect(lambda v: setattr(self.cfg, "data_3d_plane", v))
        self.sb_data_3d_xz_mode = QtWidgets.QSpinBox(self)
        self.sb_data_3d_xz_mode.setRange(0, 1)
        self.sb_data_3d_xz_mode.setValue(self.cfg.data_3d_xz_mode)
        self.sb_data_3d_xz_mode.valueChanged.connect(lambda v: setattr(self.cfg, "data_3d_xz_mode", v))
        self.sb_data_3d_z_slice = QtWidgets.QSpinBox(self)
        self.sb_data_3d_z_slice.setRange(0, 100000)
        self.sb_data_3d_z_slice.setValue(self.cfg.data_3d_z_slice)
        self.sb_data_3d_z_slice.valueChanged.connect(lambda v: setattr(self.cfg, "data_3d_z_slice", v))
        slice_mode_layout.addWidget(QtWidgets.QLabel("Plane:"))
        slice_mode_layout.addWidget(self.cb_data_3d_plane)
        slice_mode_layout.addWidget(QtWidgets.QLabel("XZ mode:"))
        slice_mode_layout.addWidget(self.sb_data_3d_xz_mode)
        slice_mode_layout.addWidget(QtWidgets.QLabel("Z index of XY plane:"))
        slice_mode_layout.addWidget(self.sb_data_3d_z_slice)
        dh_slice_layout.addRow("Slice settings:", slice_mode_layout)
        param_handle_layout.addWidget(self.dh_slice_params)

        # Invalid-value check.
        self.cb_dh_nan = QtWidgets.QCheckBox("Invalid-value check (NaN)", self)
        self.cb_dh_nan.setChecked(self.cfg.data_nan_check)
        self.cb_dh_nan.stateChanged.connect(lambda st: setattr(self.cfg, "data_nan_check", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_nan)
        self.dh_nan_params = QtWidgets.QWidget(self)
        dh_nan_layout = QtWidgets.QFormLayout(self.dh_nan_params)
        self.cb_data_nan_precision = QtWidgets.QComboBox(self)
        self.cb_data_nan_precision.addItems(["float64", "float32"])
        self.cb_data_nan_precision.setCurrentText(self.cfg.data_nan_precision)
        self.cb_data_nan_precision.currentTextChanged.connect(
            lambda v: setattr(self.cfg, "data_nan_precision", v))
        dh_nan_layout.addRow("Parsing precision:", self.cb_data_nan_precision)
        param_handle_layout.addWidget(self.dh_nan_params)

        param_handle_layout.addWidget(
            QtWidgets.QLabel("The following features use the input folder path from the general parameters above"))
        # Multi-file extrema (boolean).
        self.cb_pjz = QtWidgets.QCheckBox("Multi-file extrema", self)
        self.cb_pjz.setChecked(self.cfg.path_extreme)
        self.cb_pjz.stateChanged.connect(lambda st: setattr(self.cfg, "path_extreme", int(bool(st))))
        param_handle_layout.addWidget(self.cb_pjz)
        # Directory-level data inspection.
        self.cb_dh_directory = QtWidgets.QCheckBox("Directory-level data inspection", self)
        self.cb_dh_directory.setChecked(self.cfg.data_directory_probe)
        self.cb_dh_directory.stateChanged.connect(
            lambda st: setattr(self.cfg, "data_directory_probe", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_directory)

        param_handle_layout.addWidget(QtWidgets.QLabel("The following features each use two input files"))
        # Element distribution comparison.
        self.cb_dh_element_compare = QtWidgets.QCheckBox("Element distribution comparison", self)
        self.cb_dh_element_compare.setChecked(self.cfg.data_element_compare)
        self.cb_dh_element_compare.stateChanged.connect(
            lambda st: setattr(self.cfg, "data_element_compare", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_element_compare)
        self.dh_element_params = QtWidgets.QWidget(self)
        dh_element_layout = QtWidgets.QFormLayout(self.dh_element_params)
        dh_element_layout.addRow(QtWidgets.QLabel("Supported file types: .bin / .txt / .dat"))
        self.le_data_element_file_1 = QtWidgets.QLineEdit(self.cfg.data_element_file_1, self)
        self.le_data_element_file_1.setReadOnly(True)
        btn_data_element_file_1 = QtWidgets.QPushButton("Select file 1", self)
        btn_data_element_file_1.clicked.connect(
            lambda: self.browse_datahandle_file(self.le_data_element_file_1, "data_element_file_1"))
        element_file_1_layout = QtWidgets.QHBoxLayout()
        element_file_1_layout.addWidget(self.le_data_element_file_1)
        element_file_1_layout.addWidget(btn_data_element_file_1)
        dh_element_layout.addRow("File 1:", element_file_1_layout)
        self.le_data_element_file_2 = QtWidgets.QLineEdit(self.cfg.data_element_file_2, self)
        self.le_data_element_file_2.setReadOnly(True)
        btn_data_element_file_2 = QtWidgets.QPushButton("Select file 2", self)
        btn_data_element_file_2.clicked.connect(
            lambda: self.browse_datahandle_file(self.le_data_element_file_2, "data_element_file_2"))
        element_file_2_layout = QtWidgets.QHBoxLayout()
        element_file_2_layout.addWidget(self.le_data_element_file_2)
        element_file_2_layout.addWidget(btn_data_element_file_2)
        dh_element_layout.addRow("File 2:", element_file_2_layout)
        element_compare_options = QtWidgets.QHBoxLayout()
        self.sb_data_element_columns = QtWidgets.QSpinBox(self)
        self.sb_data_element_columns.setRange(3, 10000)
        self.sb_data_element_columns.setValue(self.cfg.data_element_columns)
        self.sb_data_element_columns.valueChanged.connect(
            lambda v: setattr(self.cfg, "data_element_columns", v))
        self.sb_data_element_x_column = QtWidgets.QSpinBox(self)
        self.sb_data_element_x_column.setRange(1, 10000)
        self.sb_data_element_x_column.setValue(self.cfg.data_element_x_column)
        self.sb_data_element_x_column.valueChanged.connect(
            lambda v: setattr(self.cfg, "data_element_x_column", v))
        self.cb_data_element_precision = QtWidgets.QComboBox(self)
        self.cb_data_element_precision.addItems(["float64", "float32"])
        self.cb_data_element_precision.setCurrentText(self.cfg.data_element_precision)
        self.cb_data_element_precision.currentTextChanged.connect(
            lambda v: setattr(self.cfg, "data_element_precision", v))
        element_compare_options.addWidget(QtWidgets.QLabel("Total columns:"))
        element_compare_options.addWidget(self.sb_data_element_columns)
        element_compare_options.addWidget(QtWidgets.QLabel("X start column:"))
        element_compare_options.addWidget(self.sb_data_element_x_column)
        element_compare_options.addWidget(QtWidgets.QLabel("Precision:"))
        element_compare_options.addWidget(self.cb_data_element_precision)
        dh_element_layout.addRow("Comparison parameters:", element_compare_options)
        param_handle_layout.addWidget(self.dh_element_params)

        # 2D field distribution comparison.
        self.cb_dh_field_2d_compare = QtWidgets.QCheckBox("2D field distribution comparison", self)
        self.cb_dh_field_2d_compare.setChecked(self.cfg.data_field_2d_compare)
        self.cb_dh_field_2d_compare.stateChanged.connect(
            lambda st: setattr(self.cfg, "data_field_2d_compare", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_field_2d_compare)
        self.dh_field_2d_params = QtWidgets.QWidget(self)
        dh_field_2d_layout = QtWidgets.QFormLayout(self.dh_field_2d_params)
        dh_field_2d_layout.addRow(QtWidgets.QLabel("Supported file types: .bin / .txt / .dat"))
        self.le_data_field_2d_file_1 = QtWidgets.QLineEdit(self.cfg.data_field_2d_file_1, self)
        self.le_data_field_2d_file_1.setReadOnly(True)
        btn_data_field_2d_file_1 = QtWidgets.QPushButton("Select field file 1", self)
        btn_data_field_2d_file_1.clicked.connect(
            lambda: self.browse_datahandle_file(
                self.le_data_field_2d_file_1, "data_field_2d_file_1"))
        field_2d_file_1_layout = QtWidgets.QHBoxLayout()
        field_2d_file_1_layout.addWidget(self.le_data_field_2d_file_1)
        field_2d_file_1_layout.addWidget(btn_data_field_2d_file_1)
        dh_field_2d_layout.addRow("File 1:", field_2d_file_1_layout)
        self.le_data_field_2d_file_2 = QtWidgets.QLineEdit(self.cfg.data_field_2d_file_2, self)
        self.le_data_field_2d_file_2.setReadOnly(True)
        btn_data_field_2d_file_2 = QtWidgets.QPushButton("Select field file 2", self)
        btn_data_field_2d_file_2.clicked.connect(
            lambda: self.browse_datahandle_file(
                self.le_data_field_2d_file_2, "data_field_2d_file_2"))
        field_2d_file_2_layout = QtWidgets.QHBoxLayout()
        field_2d_file_2_layout.addWidget(self.le_data_field_2d_file_2)
        field_2d_file_2_layout.addWidget(btn_data_field_2d_file_2)
        dh_field_2d_layout.addRow("File 2:", field_2d_file_2_layout)
        field_2d_compare_options = QtWidgets.QHBoxLayout()
        self.sb_data_field_2d_nx = QtWidgets.QSpinBox(self)
        self.sb_data_field_2d_nx.setRange(1, 100000)
        self.sb_data_field_2d_nx.setValue(self.cfg.data_field_2d_nx)
        self.sb_data_field_2d_nx.valueChanged.connect(
            lambda v: setattr(self.cfg, "data_field_2d_nx", v))
        self.sb_data_field_2d_ny = QtWidgets.QSpinBox(self)
        self.sb_data_field_2d_ny.setRange(1, 100000)
        self.sb_data_field_2d_ny.setValue(self.cfg.data_field_2d_ny)
        self.sb_data_field_2d_ny.valueChanged.connect(
            lambda v: setattr(self.cfg, "data_field_2d_ny", v))
        self.cb_data_field_2d_precision = QtWidgets.QComboBox(self)
        self.cb_data_field_2d_precision.addItems(["float64", "float32"])
        self.cb_data_field_2d_precision.setCurrentText(self.cfg.data_field_2d_precision)
        self.cb_data_field_2d_precision.currentTextChanged.connect(
            lambda v: setattr(self.cfg, "data_field_2d_precision", v))
        field_2d_compare_options.addWidget(QtWidgets.QLabel("NX:"))
        field_2d_compare_options.addWidget(self.sb_data_field_2d_nx)
        field_2d_compare_options.addWidget(QtWidgets.QLabel("NY:"))
        field_2d_compare_options.addWidget(self.sb_data_field_2d_ny)
        field_2d_compare_options.addWidget(QtWidgets.QLabel("Precision:"))
        field_2d_compare_options.addWidget(self.cb_data_field_2d_precision)
        dh_field_2d_layout.addRow("Field resolution:", field_2d_compare_options)
        param_handle_layout.addWidget(self.dh_field_2d_params)

        # 3D field distribution comparison.
        self.cb_dh_field_compare = QtWidgets.QCheckBox("3D field distribution comparison", self)
        self.cb_dh_field_compare.setChecked(self.cfg.data_field_compare)
        self.cb_dh_field_compare.stateChanged.connect(
            lambda st: setattr(self.cfg, "data_field_compare", int(bool(st))))
        param_handle_layout.addWidget(self.cb_dh_field_compare)
        self.dh_field_params = QtWidgets.QWidget(self)
        dh_field_layout = QtWidgets.QFormLayout(self.dh_field_params)
        dh_field_layout.addRow(QtWidgets.QLabel("Supported file types: .bin / .txt / .dat"))
        self.le_data_field_file_1 = QtWidgets.QLineEdit(self.cfg.data_field_file_1, self)
        self.le_data_field_file_1.setReadOnly(True)
        btn_data_field_file_1 = QtWidgets.QPushButton("Select field file 1", self)
        btn_data_field_file_1.clicked.connect(
            lambda: self.browse_datahandle_file(self.le_data_field_file_1, "data_field_file_1"))
        field_file_1_layout = QtWidgets.QHBoxLayout()
        field_file_1_layout.addWidget(self.le_data_field_file_1)
        field_file_1_layout.addWidget(btn_data_field_file_1)
        dh_field_layout.addRow("File 1:", field_file_1_layout)
        self.le_data_field_file_2 = QtWidgets.QLineEdit(self.cfg.data_field_file_2, self)
        self.le_data_field_file_2.setReadOnly(True)
        btn_data_field_file_2 = QtWidgets.QPushButton("Select field file 2", self)
        btn_data_field_file_2.clicked.connect(
            lambda: self.browse_datahandle_file(self.le_data_field_file_2, "data_field_file_2"))
        field_file_2_layout = QtWidgets.QHBoxLayout()
        field_file_2_layout.addWidget(self.le_data_field_file_2)
        field_file_2_layout.addWidget(btn_data_field_file_2)
        dh_field_layout.addRow("File 2:", field_file_2_layout)
        field_compare_options = QtWidgets.QHBoxLayout()
        self.sb_data_field_nx = QtWidgets.QSpinBox(self)
        self.sb_data_field_nx.setRange(1, 100000)
        self.sb_data_field_nx.setValue(self.cfg.data_field_nx)
        self.sb_data_field_nx.valueChanged.connect(lambda v: setattr(self.cfg, "data_field_nx", v))
        self.sb_data_field_ny = QtWidgets.QSpinBox(self)
        self.sb_data_field_ny.setRange(1, 100000)
        self.sb_data_field_ny.setValue(self.cfg.data_field_ny)
        self.sb_data_field_ny.valueChanged.connect(lambda v: setattr(self.cfg, "data_field_ny", v))
        self.sb_data_field_nz = QtWidgets.QSpinBox(self)
        self.sb_data_field_nz.setRange(1, 100000)
        self.sb_data_field_nz.setValue(self.cfg.data_field_nz)
        self.sb_data_field_nz.valueChanged.connect(lambda v: setattr(self.cfg, "data_field_nz", v))
        self.cb_data_field_precision = QtWidgets.QComboBox(self)
        self.cb_data_field_precision.addItems(["float64", "float32"])
        self.cb_data_field_precision.setCurrentText(self.cfg.data_field_precision)
        self.cb_data_field_precision.currentTextChanged.connect(
            lambda v: setattr(self.cfg, "data_field_precision", v))
        field_compare_options.addWidget(QtWidgets.QLabel("NX:"))
        field_compare_options.addWidget(self.sb_data_field_nx)
        field_compare_options.addWidget(QtWidgets.QLabel("NY:"))
        field_compare_options.addWidget(self.sb_data_field_ny)
        field_compare_options.addWidget(QtWidgets.QLabel("NZ:"))
        field_compare_options.addWidget(self.sb_data_field_nz)
        field_compare_options.addWidget(QtWidgets.QLabel("Precision:"))
        field_compare_options.addWidget(self.cb_data_field_precision)
        dh_field_layout.addRow("Field resolution:", field_compare_options)
        param_handle_layout.addWidget(self.dh_field_params)

        def update_datahandle_options():
            self.dh_slice_params.setVisible(self.cb_dh_slice.isChecked())
            self.dh_nan_params.setVisible(self.cb_dh_nan.isChecked())
            self.dh_element_params.setVisible(self.cb_dh_element_compare.isChecked())
            self.dh_field_2d_params.setVisible(self.cb_dh_field_2d_compare.isChecked())
            self.dh_field_params.setVisible(self.cb_dh_field_compare.isChecked())

        for cb in (self.cb_dh_slice, self.cb_dh_nan,
                   self.cb_dh_element_compare, self.cb_dh_field_2d_compare,
                   self.cb_dh_field_compare):
            cb.stateChanged.connect(lambda _: update_datahandle_options())
        update_datahandle_options()
        param_layout.addWidget(self.param_handle_group)      # Add to the main layout.
        self.param_handle_group.hide()                              # Hidden by default.

        # 2D-specific parameters.
        self.param2d_group = QtWidgets.QGroupBox("2D-specific parameters", self)
        param2d_layout = QtWidgets.QFormLayout(self.param2d_group)
        # View mode (boolean/enum).
        self.cb_cyl = QtWidgets.QComboBox(self)
        self.cb_cyl.addItems(["Axial (side) view", "Front view"])
        self.cb_cyl.setCurrentIndex(self.cfg.cylindrical)
        self.cb_cyl.currentIndexChanged.connect(lambda idx: setattr(self.cfg, "cylindrical", idx))
        param2d_layout.addRow("View mode:", self.cb_cyl)
        # Logarithmic scale (boolean).
        self.chk_log = QtWidgets.QCheckBox("Use logarithmic scale", self)
        self.chk_log.setChecked(self.cfg.log_scale)
        self.chk_log.stateChanged.connect(lambda st: setattr(self.cfg, "log_scale", int(bool(st))))
        param2d_layout.addRow(self.chk_log)
        # X-axis range for 1D linear data (integer).
        self.sb_phys_sin = QtWidgets.QSpinBox(self)
        self.sb_phys_sin.setRange(0, 10000)
        self.sb_phys_sin.setValue(self.cfg.physical_Sin)
        self.sb_phys_sin.valueChanged.connect(lambda val: setattr(self.cfg, "physical_Sin", val))
        param2d_layout.addRow("Linear-data X-axis range (0 uses grid range):", self.sb_phys_sin)
        # 1. Symmetric label range (boolean) - horizontal layout.
        center_layout = QtWidgets.QHBoxLayout()
        self.chk_center_r = QtWidgets.QCheckBox("Radial R", self)
        self.chk_center_r.setChecked(self.cfg.Grid_center_R)
        self.chk_center_r.stateChanged.connect(lambda st: setattr(self.cfg, "Grid_center_R", int(bool(st))))
        center_layout.addWidget(self.chk_center_r)
        self.chk_center_z = QtWidgets.QCheckBox("Axial Z", self)
        self.chk_center_z.setChecked(self.cfg.Grid_center_Z)
        self.chk_center_z.stateChanged.connect(lambda st: setattr(self.cfg, "Grid_center_Z", int(bool(st))))
        center_layout.addWidget(self.chk_center_z)
        param2d_layout.addRow("Symmetric label range:", center_layout)
        # Tick count settings (integer).
        ticks_layout = QtWidgets.QHBoxLayout()
        ticks_layout.addWidget(QtWidgets.QLabel("X axis"))
        self.sb_ticks_x = QtWidgets.QSpinBox(self)
        self.sb_ticks_x.setRange(1, 20)
        self.sb_ticks_x.setValue(self.cfg.ticks_x)
        self.sb_ticks_x.valueChanged.connect(lambda val: setattr(self.cfg, "ticks_x", val))
        ticks_layout.addWidget(self.sb_ticks_x)
        ticks_layout.addWidget(QtWidgets.QLabel("Y axis"))
        self.sb_ticks_y = QtWidgets.QSpinBox(self)
        self.sb_ticks_y.setRange(1, 20)
        self.sb_ticks_y.setValue(self.cfg.ticks_y)
        self.sb_ticks_y.valueChanged.connect(lambda val: setattr(self.cfg, "ticks_y", val))
        ticks_layout.addWidget(self.sb_ticks_y)
        ticks_layout.addWidget(QtWidgets.QLabel("Colorbar"))
        self.sb_ticks_co = QtWidgets.QSpinBox(self)
        self.sb_ticks_co.setRange(1, 20)
        self.sb_ticks_co.setValue(self.cfg.ticks_co)
        self.sb_ticks_co.valueChanged.connect(lambda val: setattr(self.cfg, "ticks_co", val))
        ticks_layout.addWidget(self.sb_ticks_co)
        param2d_layout.addRow("Tick count settings:", ticks_layout)
        # Image title (string).
        self.le_title = QtWidgets.QLineEdit(self.cfg.title, self)
        self.le_title.editingFinished.connect(lambda: setattr(self.cfg, "title", self.le_title.text()))
        param2d_layout.addRow("Image title:", self.le_title)
        self.chk_title = QtWidgets.QCheckBox("Show image title", self)
        self.chk_title.setChecked(self.cfg.show_title)
        self.chk_title.stateChanged.connect(lambda st: setattr(self.cfg, "show_title", int(bool(st))))
        param2d_layout.addRow(self.chk_title)
        # Colorbar label (string).
        self.le_cbar = QtWidgets.QLineEdit(self.cfg.colorbar_label, self)
        self.le_cbar.editingFinished.connect(lambda: setattr(self.cfg, "colorbar_label", self.le_cbar.text()))
        param2d_layout.addRow("Colorbar label:", self.le_cbar)
        # Line name 1 in line-chart mode (string).
        self.le_line1 = QtWidgets.QLineEdit(self.cfg.Line_1, self)
        self.le_line1.editingFinished.connect(lambda: setattr(self.cfg, "Line_1", self.le_line1.text()))
        param2d_layout.addRow("Line name in two-line mode, Line_1:", self.le_line1)
        # Line name 2 in line-chart mode (string).
        self.le_line2 = QtWidgets.QLineEdit(self.cfg.Line_2, self)
        self.le_line2.editingFinished.connect(lambda: setattr(self.cfg, "Line_2", self.le_line2.text()))
        param2d_layout.addRow("Line name in two-line mode, Line_2:", self.le_line2)
        # X reference-line positions (0 disables them) (float).
        x_cutoff_layout = QtWidgets.QHBoxLayout()
        x_cutoff_layout.addWidget(QtWidgets.QLabel("x1:"))
        self.ds_cut_x1 = QtWidgets.QDoubleSpinBox(self)
        self.ds_cut_x1.setDecimals(4)
        self.ds_cut_x1.setRange(-1e30, 1e30)
        self.ds_cut_x1.setSingleStep(0.0001)
        self.ds_cut_x1.setValue(self.cfg.cutoff_x1)
        self.ds_cut_x1.valueChanged.connect(lambda val: setattr(self.cfg, "cutoff_x1", val))
        x_cutoff_layout.addWidget(self.ds_cut_x1)
        x_cutoff_layout.addWidget(QtWidgets.QLabel("x2:"))
        self.ds_cut_x2 = QtWidgets.QDoubleSpinBox(self)
        self.ds_cut_x2.setDecimals(4)
        self.ds_cut_x2.setRange(-1e30, 1e30)
        self.ds_cut_x2.setSingleStep(0.0001)
        self.ds_cut_x2.setValue(self.cfg.cutoff_x2)
        self.ds_cut_x2.valueChanged.connect(lambda val: setattr(self.cfg, "cutoff_x2", val))
        x_cutoff_layout.addWidget(self.ds_cut_x2)
        param2d_layout.addRow("X reference-line positions (0 disables):", x_cutoff_layout)
        # Y reference-line positions (0 disables them) (float).
        y_cutoff_layout = QtWidgets.QHBoxLayout()
        y_cutoff_layout.addWidget(QtWidgets.QLabel("y1:"))
        self.ds_cut_y1 = QtWidgets.QDoubleSpinBox(self)
        self.ds_cut_y1.setDecimals(4)
        self.ds_cut_y1.setRange(-1e30, 1e30)
        self.ds_cut_y1.setValue(self.cfg.cutoff_y1)
        self.ds_cut_y1.valueChanged.connect(lambda val: setattr(self.cfg, "cutoff_y1", val))
        y_cutoff_layout.addWidget(self.ds_cut_y1)
        y_cutoff_layout.addWidget(QtWidgets.QLabel("y2:"))
        self.ds_cut_y2 = QtWidgets.QDoubleSpinBox(self)
        self.ds_cut_y2.setDecimals(4)
        self.ds_cut_y2.setRange(-1e30, 1e30)
        self.ds_cut_y2.setValue(self.cfg.cutoff_y2)
        self.ds_cut_y2.valueChanged.connect(lambda val: setattr(self.cfg, "cutoff_y2", val))
        y_cutoff_layout.addWidget(self.ds_cut_y2)
        param2d_layout.addRow("Y reference-line positions (0 disables):", y_cutoff_layout)
        # Region-coloring switch (boolean).
        self.chk_color_co = QtWidgets.QCheckBox("Color X region (for reference lines)", self)
        self.chk_color_co.setChecked(self.cfg.color_co)
        self.chk_color_co.stateChanged.connect(lambda st: setattr(self.cfg, "color_co", int(bool(st))))
        param2d_layout.addRow(self.chk_color_co)
        param_layout.addWidget(self.param2d_group)      # Add the 2D-specific parameter area to the main layout.
        self.param2d_group.hide()                       # Hidden by default.

        # GIF_2D-specific parameters.
        self.param_gif2d_group = QtWidgets.QGroupBox("GIF 2D-specific parameters", self)
        param_gif2d_layout = QtWidgets.QFormLayout(self.param_gif2d_group)
        # Frames per second (integer).
        self.sb_gif2d_fps = QtWidgets.QSpinBox(self)
        self.sb_gif2d_fps.setRange(1, 30)
        self.sb_gif2d_fps.setValue(self.cfg.FPS)
        self.sb_gif2d_fps.valueChanged.connect(lambda v: setattr(self.cfg, "FPS", v))
        param_gif2d_layout.addRow("FPS:", self.sb_gif2d_fps)
        # Output image size and resolution.
        gif_size_layout = QtWidgets.QHBoxLayout()
        self.ds_gif_width = QtWidgets.QDoubleSpinBox(self)
        self.ds_gif_width.setRange(1.0, 30.0)
        self.ds_gif_width.setDecimals(1)
        self.ds_gif_width.setSingleStep(0.5)
        self.ds_gif_width.setValue(self.cfg.gif_fig_width)
        self.ds_gif_width.valueChanged.connect(lambda v: setattr(self.cfg, "gif_fig_width", v))
        self.ds_gif_height = QtWidgets.QDoubleSpinBox(self)
        self.ds_gif_height.setRange(1.0, 30.0)
        self.ds_gif_height.setDecimals(1)
        self.ds_gif_height.setSingleStep(0.5)
        self.ds_gif_height.setValue(self.cfg.gif_fig_height)
        self.ds_gif_height.valueChanged.connect(lambda v: setattr(self.cfg, "gif_fig_height", v))
        self.sb_gif_dpi = QtWidgets.QSpinBox(self)
        self.sb_gif_dpi.setRange(50, 600)
        self.sb_gif_dpi.setValue(self.cfg.gif_dpi)
        self.sb_gif_dpi.valueChanged.connect(lambda v: setattr(self.cfg, "gif_dpi", v))
        gif_size_layout.addWidget(QtWidgets.QLabel("Width:"))
        gif_size_layout.addWidget(self.ds_gif_width)
        gif_size_layout.addWidget(QtWidgets.QLabel("Height:"))
        gif_size_layout.addWidget(self.ds_gif_height)
        gif_size_layout.addWidget(QtWidgets.QLabel("DPI:"))
        gif_size_layout.addWidget(self.sb_gif_dpi)
        param_gif2d_layout.addRow("Output size (inches):", gif_size_layout)
        # View mode (enum).
        self.cb_cyl_g = QtWidgets.QComboBox(self)
        self.cb_cyl_g.addItems(["Axial (side) view", "Front view"])
        self.cb_cyl_g.setCurrentIndex(self.cfg.cylindrical_g)
        self.cb_cyl_g.currentIndexChanged.connect(lambda i: setattr(self.cfg, "cylindrical_g", i))
        param_gif2d_layout.addRow("View mode:", self.cb_cyl_g)
        # Symmetric label range.
        center_g_layout = QtWidgets.QHBoxLayout()
        self.chk_center_r_g = QtWidgets.QCheckBox("Radial R", self)
        self.chk_center_r_g.setChecked(self.cfg.Grid_center_R_g)
        self.chk_center_r_g.stateChanged.connect(
            lambda st: setattr(self.cfg, "Grid_center_R_g", int(bool(st))))
        center_g_layout.addWidget(self.chk_center_r_g)
        self.chk_center_z_g = QtWidgets.QCheckBox("Axial Z", self)
        self.chk_center_z_g.setChecked(self.cfg.Grid_center_Z_g)
        self.chk_center_z_g.stateChanged.connect(
            lambda st: setattr(self.cfg, "Grid_center_Z_g", int(bool(st))))
        center_g_layout.addWidget(self.chk_center_z_g)
        param_gif2d_layout.addRow("Symmetric label range:", center_g_layout)
        # X-axis label (string).
        self.le_xlabel_g = QtWidgets.QLineEdit(self.cfg.xlabel_g, self)
        self.le_xlabel_g.editingFinished.connect(lambda: setattr(self.cfg, "xlabel_g", self.le_xlabel_g.text()))
        param_gif2d_layout.addRow("X-axis label:", self.le_xlabel_g)
        # Y-axis label (string).
        self.le_ylabel_g = QtWidgets.QLineEdit(self.cfg.ylabel_g, self)
        self.le_ylabel_g.editingFinished.connect(lambda: setattr(self.cfg, "ylabel_g", self.le_ylabel_g.text()))
        param_gif2d_layout.addRow("Y-axis label:", self.le_ylabel_g)
        # Colorbar label (string).
        self.le_cbar_g = QtWidgets.QLineEdit(self.cfg.colorbar_label_g, self)
        self.le_cbar_g.editingFinished.connect(lambda: setattr(self.cfg, "colorbar_label_g", self.le_cbar_g.text()))
        param_gif2d_layout.addRow("Colorbar label:", self.le_cbar_g)
        # Tick count settings.
        gif_ticks_layout = QtWidgets.QHBoxLayout()
        gif_ticks_layout.addWidget(QtWidgets.QLabel("X axis:"))
        self.sb_ticks_x_g = QtWidgets.QSpinBox(self)
        self.sb_ticks_x_g.setRange(1, 50)
        self.sb_ticks_x_g.setValue(self.cfg.ticks_x_g)
        self.sb_ticks_x_g.valueChanged.connect(lambda v: setattr(self.cfg, "ticks_x_g", v))
        gif_ticks_layout.addWidget(self.sb_ticks_x_g)
        gif_ticks_layout.addWidget(QtWidgets.QLabel("Y axis:"))
        self.sb_ticks_y_g = QtWidgets.QSpinBox(self)
        self.sb_ticks_y_g.setRange(1, 50)
        self.sb_ticks_y_g.setValue(self.cfg.ticks_y_g)
        self.sb_ticks_y_g.valueChanged.connect(lambda v: setattr(self.cfg, "ticks_y_g", v))
        gif_ticks_layout.addWidget(self.sb_ticks_y_g)
        gif_ticks_layout.addWidget(QtWidgets.QLabel("Colorbar:"))
        self.sb_ticks_co_g = QtWidgets.QSpinBox(self)
        self.sb_ticks_co_g.setRange(1, 50)
        self.sb_ticks_co_g.setValue(self.cfg.ticks_co_g)
        self.sb_ticks_co_g.valueChanged.connect(lambda v: setattr(self.cfg, "ticks_co_g", v))
        gif_ticks_layout.addWidget(self.sb_ticks_co_g)
        param_gif2d_layout.addRow("Tick count settings:", gif_ticks_layout)
        # Title.
        self.le_title_g = QtWidgets.QLineEdit(self.cfg.title_g, self)
        self.le_title_g.setPlaceholderText("Leave blank to use the current frame filename")
        self.le_title_g.editingFinished.connect(lambda: setattr(self.cfg, "title_g", self.le_title_g.text()))
        param_gif2d_layout.addRow("Image title:", self.le_title_g)
        self.chk_title_g = QtWidgets.QCheckBox("Show title", self)
        self.chk_title_g.setChecked(self.cfg.show_title_g)
        self.chk_title_g.stateChanged.connect(lambda st: setattr(self.cfg, "show_title_g", int(bool(st))))
        param_gif2d_layout.addRow(self.chk_title_g)
        # Logarithmic scale (boolean).
        self.chk_log_g = QtWidgets.QCheckBox("Use logarithmic scale", self)
        self.chk_log_g.setChecked(self.cfg.log_scale_g)
        self.chk_log_g.stateChanged.connect(lambda st: setattr(self.cfg, "log_scale_g", int(bool(st))))
        param_gif2d_layout.addRow(self.chk_log_g)
        # Manual-range switch (boolean).
        self.chk_manual_range = QtWidgets.QCheckBox("Custom global range", self)
        self.chk_manual_range.setChecked(self.cfg.use_manual_range)
        self.chk_manual_range.stateChanged.connect(lambda st: setattr(self.cfg, "use_manual_range", int(bool(st))))
        param_gif2d_layout.addRow(self.chk_manual_range)
        # Manual minimum/maximum values (float).
        self.ds_manual_min = QtWidgets.QDoubleSpinBox(self)
        self.ds_manual_min.setDecimals(8)
        self.ds_manual_min.setRange(-1e30, 1e30)
        self.ds_manual_min.setValue(self.cfg.manual_min)
        self.ds_manual_min.valueChanged.connect(lambda v: setattr(self.cfg, "manual_min", v))
        param_gif2d_layout.addRow("min:", self.ds_manual_min)
        self.ds_manual_max = QtWidgets.QDoubleSpinBox(self)
        self.ds_manual_max.setDecimals(8)
        self.ds_manual_max.setRange(-1e30, 1e30)
        self.ds_manual_max.setValue(self.cfg.manual_max)
        self.ds_manual_max.valueChanged.connect(lambda v: setattr(self.cfg, "manual_max", v))
        param_gif2d_layout.addRow("max:", self.ds_manual_max)
        param_layout.addWidget(self.param_gif2d_group)
        self.param_gif2d_group.hide()

        # single_array_line-specific parameters.
        self.param_single_line_group = QtWidgets.QGroupBox("Array row/column extraction line-chart parameters", self)
        param_single_layout = QtWidgets.QFormLayout(self.param_single_line_group)
        # Extraction mode (enum).
        self.cb_choice_col_ro = QtWidgets.QComboBox(self)
        self.cb_choice_col_ro.addItems(["Extract columns", "Extract rows"])
        self.cb_choice_col_ro.setCurrentIndex(self.cfg.choice_col_ro)
        self.cb_choice_col_ro.currentIndexChanged.connect(lambda i: setattr(self.cfg, "choice_col_ro", i))
        param_single_layout.addRow("Extraction mode:", self.cb_choice_col_ro)
        # Selected grid index (integer).
        self.sp_choice_single_num = QtWidgets.QSpinBox(self)
        self.sp_choice_single_num.setRange(1, 1000)
        self.sp_choice_single_num.setValue(self.cfg.choice_single_num)
        self.sp_choice_single_num.valueChanged.connect(lambda v: setattr(self.cfg, "choice_single_num", v))
        param_single_layout.addRow("Selected grid index:", self.sp_choice_single_num)
        # Tick count settings (horizontal layout).
        ticks_layout = QtWidgets.QHBoxLayout()
        # X-axis tick count (integer).
        ticks_layout.addWidget(QtWidgets.QLabel("X axis:"))
        self.sp_single_ticks_x = QtWidgets.QSpinBox(self)
        self.sp_single_ticks_x.setRange(1, 50)
        self.sp_single_ticks_x.setValue(self.cfg.single_ticks_x)
        self.sp_single_ticks_x.valueChanged.connect(lambda v: setattr(self.cfg, "single_ticks_x", v))
        ticks_layout.addWidget(self.sp_single_ticks_x)
        # Y-axis tick count (integer).
        ticks_layout.addWidget(QtWidgets.QLabel("Y axis:"))
        self.sp_single_ticks_y = QtWidgets.QSpinBox(self)
        self.sp_single_ticks_y.setRange(1, 50)
        self.sp_single_ticks_y.setValue(self.cfg.single_ticks_y)
        self.sp_single_ticks_y.valueChanged.connect(lambda v: setattr(self.cfg, "single_ticks_y", v))
        ticks_layout.addWidget(self.sp_single_ticks_y)
        param_single_layout.addRow("Tick count settings:", ticks_layout)
        # X-axis physical range (float).
        self.ds_single_range_x = QtWidgets.QDoubleSpinBox(self)
        self.ds_single_range_x.setRange(0.0, 100)
        self.ds_single_range_x.setDecimals(4)
        self.ds_single_range_x.setValue(self.cfg.single_range_x)
        self.ds_single_range_x.valueChanged.connect(lambda v: setattr(self.cfg, "single_range_x", v))
        param_single_layout.addRow("X-axis physical range (0 uses grid range):", self.ds_single_range_x)
        # Show the X-axis center.
        self.ds_center_range_x = QtWidgets.QCheckBox("X-axis data center symmetry", self)
        self.ds_center_range_x.setChecked(self.cfg.center_range_x)
        self.ds_center_range_x.stateChanged.connect(lambda checked: setattr(self.cfg, "center_range_x", int(bool(checked))))
        param_single_layout.addRow(self.ds_center_range_x)
        # Reference-line settings (horizontal layout).
        cutoff_layout = QtWidgets.QHBoxLayout()
        # X-axis reference line (0 disables it).
        cutoff_layout.addWidget(QtWidgets.QLabel("X axis:"))
        self.ds_single_cutoff_x = QtWidgets.QDoubleSpinBox(self)
        self.ds_single_cutoff_x.setRange(-1000, 1000)
        self.ds_single_cutoff_x.setDecimals(4)
        self.ds_single_cutoff_x.setValue(self.cfg.single_cutoff_x)
        self.ds_single_cutoff_x.valueChanged.connect(lambda v: setattr(self.cfg, "single_cutoff_x", v))
        cutoff_layout.addWidget(self.ds_single_cutoff_x)
        # Y-axis reference line (0 disables it).
        cutoff_layout.addWidget(QtWidgets.QLabel("Y axis:"))
        self.ds_single_cutoff_y = QtWidgets.QDoubleSpinBox(self)
        self.ds_single_cutoff_y.setRange(-1e30, 1e30)
        self.ds_single_cutoff_y.setDecimals(6)
        self.ds_single_cutoff_y.setValue(self.cfg.single_cutoff_y)
        self.ds_single_cutoff_y.valueChanged.connect(lambda v: setattr(self.cfg, "single_cutoff_y", v))
        cutoff_layout.addWidget(self.ds_single_cutoff_y)
        param_single_layout.addRow("Reference-line settings (0 disables):", cutoff_layout)
        # X-axis reference-line label (string).
        self.le_single_cutoff_x_label = QtWidgets.QLineEdit(self.cfg.single_cutoff_x_lable, self)
        self.le_single_cutoff_x_label.editingFinished.connect(
            lambda: setattr(self.cfg, "single_cutoff_x_lable", self.le_single_cutoff_x_label.text()))
        param_single_layout.addRow("X-axis reference-line label:", self.le_single_cutoff_x_label)
        # Y-axis reference-line label (string).
        self.le_single_cutoff_y_label = QtWidgets.QLineEdit(self.cfg.single_cutoff_y_lable, self)
        self.le_single_cutoff_y_label.editingFinished.connect(
            lambda: setattr(self.cfg, "single_cutoff_y_lable", self.le_single_cutoff_y_label.text()))
        param_single_layout.addRow("Y-axis reference-line label:", self.le_single_cutoff_y_label)
        # Show extrema in the legend.
        self.ds_Extreme_value = QtWidgets.QCheckBox("Show extrema", self)
        self.ds_Extreme_value.setChecked(self.cfg.single_Extreme_value)
        self.ds_Extreme_value.stateChanged.connect(lambda st: setattr(self.cfg, "single_Extreme_value", int(bool(st))))
        param_single_layout.addRow(self.ds_Extreme_value)
        # Chart title (string).
        self.le_single_title = QtWidgets.QLineEdit(self.cfg.single_title, self)
        self.le_single_title.editingFinished.connect(
            lambda: setattr(self.cfg, "single_title", self.le_single_title.text()))
        param_single_layout.addRow("Chart title:", self.le_single_title)
        param_layout.addWidget(self.param_single_line_group)
        self.param_single_line_group.hide()

        # point_Selection-specific parameters.
        self.param_point_group = QtWidgets.QGroupBox("Selected-point data evolution parameters", self)
        param_point_layout = QtWidgets.QFormLayout(self.param_point_group)
        # Point coordinate NR (integer).
        self.sb_point_nr = QtWidgets.QSpinBox(self)
        self.sb_point_nr.setRange(0, 10000)
        self.sb_point_nr.setValue(self.cfg.point_coords[0])
        self.sb_point_nr.valueChanged.connect(lambda v: setattr(self.cfg, "point_coords", (v, self.cfg.point_coords[1])))
        param_point_layout.addRow("NR grid coordinate:", self.sb_point_nr)
        # Point coordinate NTH (integer).
        self.sb_point_nth = QtWidgets.QSpinBox(self)
        self.sb_point_nth.setRange(0, 10000)
        self.sb_point_nth.setValue(self.cfg.point_coords[1])
        self.sb_point_nth.valueChanged.connect(lambda v: setattr(self.cfg, "point_coords", (self.cfg.point_coords[0], v)))
        param_point_layout.addRow("NZ/NTH grid coordinate:", self.sb_point_nth)
        # View mode (enum).
        self.cb_cyl_point = QtWidgets.QComboBox(self)
        self.cb_cyl_point.addItems(["Axial (side) view", "Front view"])
        self.cb_cyl_point.setCurrentIndex(self.cfg.cylindrical_point)
        self.cb_cyl_point.currentIndexChanged.connect(lambda i: setattr(self.cfg, "cylindrical_point", i))
        param_point_layout.addRow("View mode:", self.cb_cyl_point)
        # Y-axis label (string).
        self.le_ylabel_ps = QtWidgets.QLineEdit(self.cfg.ylabel_ps, self)
        self.le_ylabel_ps.editingFinished.connect(lambda: setattr(self.cfg, "ylabel_ps", self.le_ylabel_ps.text()))
        param_point_layout.addRow("Y-axis label:", self.le_ylabel_ps)
        param_layout.addWidget(self.param_point_group)
        self.param_point_group.hide()

        # part_traj-specific parameters.
        self.param_part_traj_group = QtWidgets.QGroupBox("Particle trajectory/scatter parameters", self)
        param_part_traj_layout = QtWidgets.QFormLayout(self.param_part_traj_group)
        # Display mode (enum).
        self.cb_paradigm_pt = QtWidgets.QComboBox(self)
        self.cb_paradigm_pt.addItems(["Single-particle trajectory", "Multi-particle scatter (beam)"])
        self.cb_paradigm_pt.setCurrentIndex(self.cfg.paradigm_pt)
        self.cb_paradigm_pt.currentIndexChanged.connect(lambda i: setattr(self.cfg, "paradigm_pt", i))
        param_part_traj_layout.addRow("Display mode:", self.cb_paradigm_pt)
        # X-coordinate column (integer).
        self.cb_x_columns_pt = QtWidgets.QSpinBox(self)
        self.cb_x_columns_pt.setRange(1, 10)
        self.cb_x_columns_pt.setValue(self.cfg.x_columns_pt)
        self.cb_x_columns_pt.valueChanged.connect(lambda v: setattr(self.cfg, "x_columns_pt", v))
        param_part_traj_layout.addRow("X-coordinate column (if 1, Y/Z are in columns 2/3):", self.cb_x_columns_pt)
        # Display radius (float).
        self.dsb_R_pt = QtWidgets.QDoubleSpinBox(self)
        self.dsb_R_pt.setDecimals(3)
        self.dsb_R_pt.setRange(0.01, 5.0)
        self.dsb_R_pt.setSingleStep(0.01)
        self.dsb_R_pt.setValue(self.cfg.R_pt)
        self.dsb_R_pt.valueChanged.connect(lambda v: setattr(self.cfg, "R_pt", v))
        param_part_traj_layout.addRow("Display radius (m):", self.dsb_R_pt)
        # Z-axis range settings (horizontal layout).
        z_range_layout = QtWidgets.QHBoxLayout()
        # Z-axis minimum (float).
        z_range_layout.addWidget(QtWidgets.QLabel("Left (m):"))
        self.dsb_z_min_pt = QtWidgets.QDoubleSpinBox(self)
        self.dsb_z_min_pt.setDecimals(3)
        self.dsb_z_min_pt.setRange(-10.0, 10.0)
        self.dsb_z_min_pt.setSingleStep(0.01)
        self.dsb_z_min_pt.setValue(self.cfg.z_min_pt)
        self.dsb_z_min_pt.valueChanged.connect(lambda v: setattr(self.cfg, "z_min_pt", v))
        z_range_layout.addWidget(self.dsb_z_min_pt)
        # Z-axis maximum (float).
        z_range_layout.addWidget(QtWidgets.QLabel("Right (m):"))
        self.dsb_z_max_pt = QtWidgets.QDoubleSpinBox(self)
        self.dsb_z_max_pt.setDecimals(3)
        self.dsb_z_max_pt.setRange(-10.0, 10.0)
        self.dsb_z_max_pt.setSingleStep(0.01)
        self.dsb_z_max_pt.setValue(self.cfg.z_max_pt)
        self.dsb_z_max_pt.valueChanged.connect(lambda v: setattr(self.cfg, "z_max_pt", v))
        z_range_layout.addWidget(self.dsb_z_max_pt)
        param_part_traj_layout.addRow("Device length range:", z_range_layout)
        # Device-shell transparency (float).
        self.dsb_e_alpha_pt = QtWidgets.QDoubleSpinBox(self)
        self.dsb_e_alpha_pt.setDecimals(2)
        self.dsb_e_alpha_pt.setRange(0.0, 1.0)
        self.dsb_e_alpha_pt.setSingleStep(0.05)
        self.dsb_e_alpha_pt.setValue(self.cfg.e_alpha_pt)
        self.dsb_e_alpha_pt.valueChanged.connect(lambda v: setattr(self.cfg, "e_alpha_pt", v))
        param_part_traj_layout.addRow("Shell transparency:", self.dsb_e_alpha_pt)
        # Trajectory line width (integer).
        self.sb_tlw_pt = QtWidgets.QSpinBox(self)
        self.sb_tlw_pt.setRange(1, 5)
        self.sb_tlw_pt.setValue(self.cfg.tlw_pt)
        self.sb_tlw_pt.valueChanged.connect(lambda v: setattr(self.cfg, "tlw_pt", v))
        param_part_traj_layout.addRow("Trajectory line width:", self.sb_tlw_pt)
        # Particle marker size (integer).
        self.sb_ps_pt = QtWidgets.QSpinBox(self)
        self.sb_ps_pt.setRange(1, 100)
        self.sb_ps_pt.setValue(self.cfg.ps_pt)
        self.sb_ps_pt.valueChanged.connect(lambda v: setattr(self.cfg, "ps_pt", v))
        param_part_traj_layout.addRow("Particle marker size:", self.sb_ps_pt)
        # Tick count settings.
        self.ticks_layout = QtWidgets.QHBoxLayout()
        # Z axis (new mapping).
        self.sb_x_ticks_num_pt = QtWidgets.QSpinBox(self)
        self.sb_x_ticks_num_pt.setRange(0, 20)
        self.sb_x_ticks_num_pt.setValue(self.cfg.x_ticks_num_pt)
        self.sb_x_ticks_num_pt.valueChanged.connect(lambda v: setattr(self.cfg, "x_ticks_num_pt", v))
        self.ticks_layout.addWidget(QtWidgets.QLabel("Z axis:"))
        self.ticks_layout.addWidget(self.sb_x_ticks_num_pt)
        # Y axis.
        self.sb_y_ticks_num_pt = QtWidgets.QSpinBox(self)
        self.sb_y_ticks_num_pt.setRange(0, 20)
        self.sb_y_ticks_num_pt.setValue(self.cfg.y_ticks_num_pt)
        self.sb_y_ticks_num_pt.valueChanged.connect(lambda v: setattr(self.cfg, "y_ticks_num_pt", v))
        self.ticks_layout.addWidget(QtWidgets.QLabel("Y axis:"))
        self.ticks_layout.addWidget(self.sb_y_ticks_num_pt)
        # X axis.
        self.sb_z_ticks_num_pt = QtWidgets.QSpinBox(self)
        self.sb_z_ticks_num_pt.setRange(0, 20)
        self.sb_z_ticks_num_pt.setValue(self.cfg.z_ticks_num_pt)
        self.sb_z_ticks_num_pt.valueChanged.connect(lambda v: setattr(self.cfg, "z_ticks_num_pt", v))
        self.ticks_layout.addWidget(QtWidgets.QLabel("X axis:"))
        self.ticks_layout.addWidget(self.sb_z_ticks_num_pt)
        param_part_traj_layout.addRow("Tick count per axis:", self.ticks_layout)
        param_layout.addWidget(self.param_part_traj_group)
        self.param_part_traj_group.hide()
        # Colorbar tick count (integer).
        self.sb_c_num_pt = QtWidgets.QSpinBox(self)
        self.sb_c_num_pt.setRange(1, 10)
        self.sb_c_num_pt.setValue(self.cfg.c_num_pt)
        self.sb_c_num_pt.valueChanged.connect(lambda v: setattr(self.cfg, "c_num_pt", v))
        param_part_traj_layout.addRow("Colorbar tick count:", self.sb_c_num_pt)
        # Colorbar name (string).
        self.le_c_name_pt = QtWidgets.QLineEdit(self.cfg.c_name_pt, self)
        self.le_c_name_pt.editingFinished.connect(lambda: setattr(self.cfg, "c_name_pt", self.le_c_name_pt.text()))
        param_part_traj_layout.addRow("Colorbar name:", self.le_c_name_pt)
        # Load background field (boolean).
        self.chk_add_field_pt = QtWidgets.QCheckBox("Load background field data", self)
        self.chk_add_field_pt.setChecked(bool(self.cfg.add_field_pt))
        self.chk_add_field_pt.stateChanged.connect(lambda st: setattr(self.cfg, "add_field_pt", int(bool(st))))
        param_part_traj_layout.addRow(self.chk_add_field_pt)
        # Background field file (string + file selector).
        self.field_file_layout = QtWidgets.QHBoxLayout()
        self.le_field_filename = QtWidgets.QLineEdit(self.cfg.field_filename, self)
        self.le_field_filename.editingFinished.connect(
            lambda: setattr(self.cfg, "field_filename", self.le_field_filename.text()))
        self.btn_field_browse = QtWidgets.QPushButton("select...", self)
        self.btn_field_browse.clicked.connect(self.browse_field_file)
        self.field_file_layout.addWidget(self.le_field_filename)
        self.field_file_layout.addWidget(self.btn_field_browse)
        param_part_traj_layout.addRow("Background field file:", self.field_file_layout)
        # Background field transparency (float).
        self.dsb_field_alpha_pt = QtWidgets.QDoubleSpinBox(self)
        self.dsb_field_alpha_pt.setDecimals(2)
        self.dsb_field_alpha_pt.setRange(0.0, 1.0)
        self.dsb_field_alpha_pt.setSingleStep(0.05)
        self.dsb_field_alpha_pt.setValue(self.cfg.field_alpha_pt)
        self.dsb_field_alpha_pt.valueChanged.connect(lambda v: setattr(self.cfg, "field_alpha_pt", v))
        param_part_traj_layout.addRow("Background field transparency:", self.dsb_field_alpha_pt)
        # Background field shape (two integers).
        self.field_shape_layout = QtWidgets.QHBoxLayout()
        self.sb_field_shape_x = QtWidgets.QSpinBox(self)
        self.sb_field_shape_x.setRange(1, 1000)
        self.sb_field_shape_x.setValue(self.cfg.field_shape_pt[0])
        self.sb_field_shape_x.valueChanged.connect(self.update_field_shape)
        self.sb_field_shape_y = QtWidgets.QSpinBox(self)
        self.sb_field_shape_y.setRange(1, 1000)
        self.sb_field_shape_y.setValue(self.cfg.field_shape_pt[1])
        self.sb_field_shape_y.valueChanged.connect(self.update_field_shape)
        self.field_shape_layout.addWidget(QtWidgets.QLabel("X:"))
        self.field_shape_layout.addWidget(self.sb_field_shape_x)
        self.field_shape_layout.addWidget(QtWidgets.QLabel("Y:"))
        self.field_shape_layout.addWidget(self.sb_field_shape_y)
        param_part_traj_layout.addRow("Background field file shape:", self.field_shape_layout)

        # part_traj_gif-specific parameters.
        self.param_part_traj_gif_group = QtWidgets.QGroupBox("Particle trajectory/scatter GIF parameters", self)
        param_part_traj_gif_layout = QtWidgets.QFormLayout(self.param_part_traj_gif_group)
        # Display mode (enum).
        self.cb_paradigm_ptg = QtWidgets.QComboBox(self)
        self.cb_paradigm_ptg.addItems(["Single-particle trajectory", "Multi-particle scatter (beam)"])
        self.cb_paradigm_ptg.setCurrentIndex(self.cfg.paradigm_ptg)
        self.cb_paradigm_ptg.currentIndexChanged.connect(lambda i: setattr(self.cfg, "paradigm_ptg", i))
        param_part_traj_gif_layout.addRow("Display mode:", self.cb_paradigm_ptg)
        # X-coordinate column (integer).
        self.cb_x_columns_ptg = QtWidgets.QSpinBox(self)
        self.cb_x_columns_ptg.setRange(1, 10)
        self.cb_x_columns_ptg.setValue(self.cfg.x_columns_ptg)
        self.cb_x_columns_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "x_columns_ptg", v))
        param_part_traj_gif_layout.addRow("X-coordinate column (if 1, Y/Z are in columns 2/3):", self.cb_x_columns_ptg)
        # Animation frame rate (integer).
        self.sb_fps_ptg = QtWidgets.QSpinBox(self)
        self.sb_fps_ptg.setRange(5, 60)
        self.sb_fps_ptg.setValue(self.cfg.fps_ptg)
        self.sb_fps_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "fps_ptg", v))
        param_part_traj_gif_layout.addRow("Frame rate (fps):", self.sb_fps_ptg)
        # GIF resolution (integer).
        self.sb_plt_dpi_ptg = QtWidgets.QSpinBox(self)
        self.sb_plt_dpi_ptg.setRange(50, 600)
        self.sb_plt_dpi_ptg.setValue(self.cfg.plt_dpi_ptg)
        self.sb_plt_dpi_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "plt_dpi_ptg", v))
        param_part_traj_gif_layout.addRow("GIF resolution (DPI):", self.sb_plt_dpi_ptg)
        # Data step (integer).
        self.sb_paint_step_ptg = QtWidgets.QSpinBox(self)
        self.sb_paint_step_ptg.setRange(10, 1000)
        self.sb_paint_step_ptg.setValue(self.cfg.paint_step_ptg)
        self.sb_paint_step_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "paint_step_ptg", v))
        param_part_traj_gif_layout.addRow("Data step (≥10); beware lag and memory exhaustion:", self.sb_paint_step_ptg)
        # Display radius (float).
        self.dsb_R_ptg = QtWidgets.QDoubleSpinBox(self)
        self.dsb_R_ptg.setDecimals(3)
        self.dsb_R_ptg.setRange(0.01, 5.0)
        self.dsb_R_ptg.setSingleStep(0.01)
        self.dsb_R_ptg.setValue(self.cfg.R_ptg)
        self.dsb_R_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "R_ptg", v))
        param_part_traj_gif_layout.addRow("Display radius (m):", self.dsb_R_ptg)
        # Z-axis range settings (horizontal layout).
        z_range_layout_ptg = QtWidgets.QHBoxLayout()
        # Z-axis minimum (float).
        z_range_layout_ptg.addWidget(QtWidgets.QLabel("Left (m):"))
        self.dsb_z_min_ptg = QtWidgets.QDoubleSpinBox(self)
        self.dsb_z_min_ptg.setDecimals(3)
        self.dsb_z_min_ptg.setRange(-10.0, 10.0)
        self.dsb_z_min_ptg.setSingleStep(0.01)
        self.dsb_z_min_ptg.setValue(self.cfg.z_min_ptg)
        self.dsb_z_min_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "z_min_ptg", v))
        z_range_layout_ptg.addWidget(self.dsb_z_min_ptg)
        # Z-axis maximum (float).
        z_range_layout_ptg.addWidget(QtWidgets.QLabel("Right (m):"))
        self.dsb_z_max_ptg = QtWidgets.QDoubleSpinBox(self)
        self.dsb_z_max_ptg.setDecimals(3)
        self.dsb_z_max_ptg.setRange(-10.0, 10.0)
        self.dsb_z_max_ptg.setSingleStep(0.01)
        self.dsb_z_max_ptg.setValue(self.cfg.z_max_ptg)
        self.dsb_z_max_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "z_max_ptg", v))
        z_range_layout_ptg.addWidget(self.dsb_z_max_ptg)
        param_part_traj_gif_layout.addRow("Device length range:", z_range_layout_ptg)
        # Device-shell transparency (float).
        self.dsb_e_alpha_ptg = QtWidgets.QDoubleSpinBox(self)
        self.dsb_e_alpha_ptg.setDecimals(2)
        self.dsb_e_alpha_ptg.setRange(0.0, 1.0)
        self.dsb_e_alpha_ptg.setSingleStep(0.05)
        self.dsb_e_alpha_ptg.setValue(self.cfg.e_alpha_ptg)
        self.dsb_e_alpha_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "e_alpha_ptg", v))
        param_part_traj_gif_layout.addRow("Shell transparency:", self.dsb_e_alpha_ptg)
        # Trajectory line width (integer).
        self.sb_tlw_ptg = QtWidgets.QSpinBox(self)
        self.sb_tlw_ptg.setRange(1, 5)
        self.sb_tlw_ptg.setValue(self.cfg.tlw_ptg)
        self.sb_tlw_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "tlw_ptg", v))
        param_part_traj_gif_layout.addRow("Trajectory line width:", self.sb_tlw_ptg)
        # Particle marker size (integer).
        self.sb_ps_ptg = QtWidgets.QSpinBox(self)
        self.sb_ps_ptg.setRange(1, 100)
        self.sb_ps_ptg.setValue(self.cfg.ps_ptg)
        self.sb_ps_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "ps_ptg", v))
        param_part_traj_gif_layout.addRow("Particle marker size:", self.sb_ps_ptg)
        # Tick count settings.
        self.ticks_layout_ptg = QtWidgets.QHBoxLayout()
        # Z axis (new mapping).
        self.sb_x_ticks_num_ptg = QtWidgets.QSpinBox(self)
        self.sb_x_ticks_num_ptg.setRange(0, 20)
        self.sb_x_ticks_num_ptg.setValue(self.cfg.x_ticks_num_ptg)
        self.sb_x_ticks_num_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "x_ticks_num_ptg", v))
        self.ticks_layout_ptg.addWidget(QtWidgets.QLabel("Z axis:"))
        self.ticks_layout_ptg.addWidget(self.sb_x_ticks_num_ptg)
        # Y axis.
        self.sb_y_ticks_num_ptg = QtWidgets.QSpinBox(self)
        self.sb_y_ticks_num_ptg.setRange(0, 20)
        self.sb_y_ticks_num_ptg.setValue(self.cfg.y_ticks_num_ptg)
        self.sb_y_ticks_num_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "y_ticks_num_ptg", v))
        self.ticks_layout_ptg.addWidget(QtWidgets.QLabel("Y axis:"))
        self.ticks_layout_ptg.addWidget(self.sb_y_ticks_num_ptg)
        # X axis.
        self.sb_z_ticks_num_ptg = QtWidgets.QSpinBox(self)
        self.sb_z_ticks_num_ptg.setRange(0, 20)
        self.sb_z_ticks_num_ptg.setValue(self.cfg.z_ticks_num_ptg)
        self.sb_z_ticks_num_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "z_ticks_num_ptg", v))
        self.ticks_layout_ptg.addWidget(QtWidgets.QLabel("X axis:"))
        self.ticks_layout_ptg.addWidget(self.sb_z_ticks_num_ptg)
        param_part_traj_gif_layout.addRow("Tick count per axis:", self.ticks_layout_ptg)
        # Colorbar tick count (integer).
        self.sb_c_num_ptg = QtWidgets.QSpinBox(self)
        self.sb_c_num_ptg.setRange(1, 10)
        self.sb_c_num_ptg.setValue(self.cfg.c_num_ptg)
        self.sb_c_num_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "c_num_ptg", v))
        param_part_traj_gif_layout.addRow("Colorbar tick count:", self.sb_c_num_ptg)
        # Colorbar name (string).
        self.le_c_name_ptg = QtWidgets.QLineEdit(self.cfg.c_name_ptg, self)
        self.le_c_name_ptg.editingFinished.connect(lambda: setattr(self.cfg, "c_name_ptg", self.le_c_name_ptg.text()))
        param_part_traj_gif_layout.addRow("Colorbar name:", self.le_c_name_ptg)
        # Load background field (boolean).
        self.chk_add_field_ptg = QtWidgets.QCheckBox("Load background field data", self)
        self.chk_add_field_ptg.setChecked(bool(self.cfg.add_field_ptg))
        self.chk_add_field_ptg.stateChanged.connect(lambda st: setattr(self.cfg, "add_field_ptg", int(bool(st))))
        param_part_traj_gif_layout.addRow(self.chk_add_field_ptg)
        # Background field file (string + file selector).
        self.field_file_layout_ptg = QtWidgets.QHBoxLayout()
        self.le_field_filename_ptg = QtWidgets.QLineEdit(self.cfg.field_filename_ptg, self)
        self.le_field_filename_ptg.editingFinished.connect(
            lambda: setattr(self.cfg, "field_filename_ptg", self.le_field_filename_ptg.text()))
        self.btn_field_browse_ptg = QtWidgets.QPushButton("select...", self)
        self.btn_field_browse_ptg.clicked.connect(self.browse_field_file_ptg)  # Correct connection.
        self.field_file_layout_ptg.addWidget(self.le_field_filename_ptg)
        self.field_file_layout_ptg.addWidget(self.btn_field_browse_ptg)
        param_part_traj_gif_layout.addRow("Background field file:", self.field_file_layout_ptg)
        # Background field transparency (float).
        self.dsb_field_alpha_ptg = QtWidgets.QDoubleSpinBox(self)
        self.dsb_field_alpha_ptg.setDecimals(2)
        self.dsb_field_alpha_ptg.setRange(0.0, 1.0)
        self.dsb_field_alpha_ptg.setSingleStep(0.05)
        self.dsb_field_alpha_ptg.setValue(self.cfg.field_alpha_ptg)
        self.dsb_field_alpha_ptg.valueChanged.connect(lambda v: setattr(self.cfg, "field_alpha_ptg", v))
        param_part_traj_gif_layout.addRow("Background field transparency:", self.dsb_field_alpha_ptg)
        # Background field shape (two integers).
        self.field_shape_layout_ptg = QtWidgets.QHBoxLayout()
        self.sb_field_shape_x_ptg = QtWidgets.QSpinBox(self)
        self.sb_field_shape_x_ptg.setRange(1, 1000)
        self.sb_field_shape_x_ptg.setValue(self.cfg.field_shape_ptg[0])
        self.sb_field_shape_x_ptg.valueChanged.connect(self.update_field_shape_ptg)  # Correct connection.
        self.sb_field_shape_y_ptg = QtWidgets.QSpinBox(self)
        self.sb_field_shape_y_ptg.setRange(1, 1000)
        self.sb_field_shape_y_ptg.setValue(self.cfg.field_shape_ptg[1])
        self.sb_field_shape_y_ptg.valueChanged.connect(self.update_field_shape_ptg)  # Correct connection.
        self.field_shape_layout_ptg.addWidget(QtWidgets.QLabel("X:"))
        self.field_shape_layout_ptg.addWidget(self.sb_field_shape_x_ptg)
        self.field_shape_layout_ptg.addWidget(QtWidgets.QLabel("Y:"))
        self.field_shape_layout_ptg.addWidget(self.sb_field_shape_y_ptg)
        param_part_traj_gif_layout.addRow("Background field file shape:", self.field_shape_layout_ptg)
        param_layout.addWidget(self.param_part_traj_gif_group)
        self.param_part_traj_gif_group.hide()

        main_layout.addWidget(param_container)      # Add the parameter area to the main layout.

        # Dynamic panel-switching logic.
        def update_specific_panel():
            self.param_handle_group.setVisible(self.cb_handle.isChecked())
            self.param2d_group.setVisible(self.cb_2d.isChecked())
            self.param_gif2d_group.setVisible(self.cb_gif2d.isChecked())
            self.param_single_line_group.setVisible(self.cb_single_line.isChecked())
            self.param_point_group.setVisible(self.cb_point_selection.isChecked())
            self.param_part_traj_group.setVisible(self.cb_part_traj.isChecked())
            self.param_part_traj_gif_group.setVisible(self.cb_part_traj_gif.isChecked())

        # Bind all feature-list checkboxes.
        for cb in (self.cb_handle,
                   self.cb_2d,
                   self.cb_gif2d,
                   self.cb_single_line,
                   self.cb_point_selection,
                   self.cb_part_traj,
                   self.cb_part_traj_gif):
            cb.stateChanged.connect(lambda _: update_specific_panel())

        update_specific_panel()     # Initialize once.
        self.btn_run = QtWidgets.QPushButton("START", self)   # Start button.
        self.btn_run.setFixedSize(100, 40)
        # Background color (hex), text color, and corner radius.
        self.btn_run.setStyleSheet("""
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            font-size: 15px;
        """)
        self.btn_run.clicked.connect(self.run_actions)
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.addWidget(self.btn_run)
        action_layout.addSpacing(24)
        action_layout.addWidget(self.btn_targo)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)

    def _append_output(self, text: str):
        cursor = self.text_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.text_output.setTextCursor(cursor)
        self.text_output.ensureCursorVisible()

    def open_targo(self):
        search_dirs = []
        bundled_dir = getattr(sys, "_MEIPASS", None)
        if bundled_dir:
            search_dirs.append(Path(bundled_dir))
        search_dirs.append(Path(__file__).resolve().parent)
        if getattr(sys, "frozen", False):
            search_dirs.append(Path(sys.executable).resolve().parent)

        html_path = next(
            (directory / "TarGo_v1.3.html" for directory in search_dirs
             if (directory / "TarGo_v1.3.html").is_file()),
            None,
        )
        if html_path is None:
            self._append_output("ERROR: TarGo_v1.3.html was not found; make sure it was packaged with the program.\n")
            return
        try:
            if not webbrowser.open_new_tab(html_path.resolve().as_uri()):
                raise RuntimeError("The system default browser did not respond")
            self._append_output(f"TarGo opened in the system default browser: {html_path}\n")
        except Exception as exc:
            self._append_output(f"ERROR: Failed to open TarGo: {exc}\n")

    def run_actions(self):
        try:
            self._append_output("-----------------------------\n")
            if self.cfg.data_handle:
                if self.cfg.data_discrete:
                    datahandle.analyze_single_file(self.cfg.input_path)
                if self.cfg.file_extreme:
                    datahandle.sub_file_extrema(self.cfg.input_path)
                if self.cfg .path_extreme:
                    datahandle.sub_path_extreme(self.cfg.file_path)
                if self.cfg.data_3d_to_2d:
                    datahandle.extract_3d_to_2d(
                        self.cfg.input_path,
                        self.cfg.output_path,
                        self.cfg.data_3d_nx,
                        self.cfg.data_3d_ny,
                        self.cfg.data_3d_nz,
                        self.cfg.data_3d_xz_mode,
                        self.cfg.data_3d_plane,
                        self.cfg.data_3d_z_slice,
                    )
                if self.cfg.data_directory_probe:
                    datahandle.inspect_directory(self.cfg.file_path)
                if self.cfg.data_nan_check:
                    datahandle.check_invalid_values(
                        self.cfg.input_path,
                        self.cfg.data_nan_precision,
                    )
                if self.cfg.data_element_compare:
                    datahandle.compare_element_distributions(
                        self.cfg.data_element_file_1,
                        self.cfg.data_element_file_2,
                        self.cfg.data_element_columns,
                        self.cfg.data_element_x_column,
                        self.cfg.data_element_precision,
                    )
                if self.cfg.data_field_2d_compare:
                    datahandle.compare_2d_fields(
                        self.cfg.data_field_2d_file_1,
                        self.cfg.data_field_2d_file_2,
                        self.cfg.data_field_2d_nx,
                        self.cfg.data_field_2d_ny,
                        self.cfg.data_field_2d_precision,
                    )
                if self.cfg.data_field_compare:
                    datahandle.compare_3d_fields(
                        self.cfg.data_field_file_1,
                        self.cfg.data_field_file_2,
                        self.cfg.data_field_nx,
                        self.cfg.data_field_ny,
                        self.cfg.data_field_nz,
                        self.cfg.data_field_precision,
                    )
            if self.cfg.dimension_2D:
                imageka.sub_dimension_2D(self.cfg)
            if self.cfg.GIF_2D:
                gifka.sub_GIF_2D(self.cfg)
            if self.cfg.single_array_line:
                waveka.sub_single_array_line(self.cfg)
            if self.cfg.point_Selection:
                waveka.sub_point_Selection(self.cfg)
            if self.cfg.part_traj:
                Particlestrajectory.plot_particles_tra(self.cfg)
            if self.cfg.part_traj_gif:
                Pandtgif.pandt_gifka(self.cfg)

            self._append_output(">>END<<\n")
        except run_DebugError.ImagekaError as e:
            self._append_output(f"ERROR: {e}\n")
        except Exception:
            buf = io.StringIO()
            traceback.print_exc(file=buf)
            self._append_output(buf.getvalue())

    def _on_input_path_click(self, event):
        # Call the native Windows file dialog.
        start_dir = QtCore.QDir.homePath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Input file", start_dir, options=QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.cfg.input_path = path  # Update cfg and display it.
            self.le_input_path.setText(path)
        return QtWidgets.QLineEdit.mousePressEvent(self.le_input_path, event)   # Pass the event to the parent class to preserve normal widget behavior.

    def _on_file_path_click(self, event):
        start_dir = QtCore.QDir.homePath()
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Input folder", start_dir, options=QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.cfg.file_path = path
            self.le_file_path.setText(path)
        return QtWidgets.QLineEdit.mousePressEvent(self.le_file_path, event)

    def _on_output_path_click(self, event):
        start_dir = QtCore.QDir.homePath()
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Output folder", start_dir, options=QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.cfg.output_path = path
            self.le_output_path.setText(path)
        return QtWidgets.QLineEdit.mousePressEvent(self.le_output_path, event)

    def browse_datahandle_file(self, line_edit, config_attr):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select data file", "", "Data Files (*.bin *.txt *.dat);;All Files (*)")
        if file_path:
            line_edit.setText(file_path)
            setattr(self.cfg, config_attr, file_path)

    def browse_field_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select background field file", "", "All Files (*);;Text Files (*.txt)")
        if file_path:
            self.le_field_filename.setText(file_path)
            self.cfg.field_filename = file_path

    def update_field_shape(self):
        x = self.sb_field_shape_x.value()
        y = self.sb_field_shape_y.value()
        self.cfg.field_shape_pt = (x, y)

    def browse_field_file_ptg(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select background field file","","All Files (*);;Text Files (*.txt);;NPY Files (*.npy)")
        if file_path:
            self.le_field_filename_ptg.setText(file_path)
            self.cfg.field_filename_ptg = file_path

    def update_field_shape_ptg(self):
        x = self.sb_field_shape_x_ptg.value()
        y = self.sb_field_shape_y_ptg.value()
        self.cfg.field_shape_ptg = (x, y)
