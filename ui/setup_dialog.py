import socket
import struct
import sys
from typing import Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


# =========================================================================
# FUNKSIONET NDIHMËSE PËR KONVERTIMIN E IP DHE TYPE
# =========================================================================
def ip_to_hex(ip_str: str) -> str:
  """Konverton '192.168.1.222' -> 'C0A801DE'"""
  try:
    packed = socket.inet_aton(ip_str.strip())
    return struct.pack("!I", struct.unpack("!I", packed)[0]).hex().upper()
  except Exception:
    return "C0A801DE"


def hex_to_ip(hex_str: str) -> str:
  """Konverton 'C0A801DE' -> '192.168.1.222' ose ruan IP-në nëse është tashmë në format pikash."""
  try:
    clean_hex = hex_str.strip()
    if "." in clean_hex:
      return clean_hex
    packed = bytes.fromhex(clean_hex)
    return socket.inet_ntoa(packed)
  except Exception:
    return "192.168.1.222"


CONTROLLER_TYPE_MAP = {
    "DEMO": 0,
    "USB-MC": 1,
    "ETH-MCI": 2,
    "ETH-MC(BOX)": 3,
}

REVERSE_CONTROLLER_MAP = {
    0: "DEMO",
    1: "USB-MC",
    2: "ETH-MCI",
    3: "ETH-MC(BOX)",
}


class GeneralSettingsWidget(QWidget):
  """Faqja General Settings."""

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager
    self.init_ui()
    self.load_settings()


  

  def init_ui(self):
    main_layout = QVBoxLayout(self)
    main_layout.setSpacing(12)
    main_layout.setContentsMargins(10, 10, 10, 10)

    # 1. G-code init string
    lbl_gcode = QLabel("G-code init string:")
    self.txt_gcode_init = QLineEdit("G17 G64 G49 G40")

    main_layout.addWidget(lbl_gcode)
    main_layout.addWidget(self.txt_gcode_init)

    # 2. Middle Row: Tool change (M6) & Laser options
    mid_layout = QHBoxLayout()

    # Tool change Group
    group_tool = QGroupBox("Tool change (M6)")
    layout_tool = QVBoxLayout()

    self.rb_ignore_tc = QRadioButton("Ignore tool change")
    self.rb_ignore_tc.setChecked(True)
    self.rb_stop_tc = QRadioButton("Stop and wait for START")

    # Location X, Y, Z layout
    pos_layout = QHBoxLayout()
    self.txt_x = QLineEdit("0")
    self.txt_y = QLineEdit("0")
    self.txt_z = QLineEdit("0")
    for txt in (self.txt_x, self.txt_y, self.txt_z):
      txt.setFixedWidth(50)

    pos_layout.addWidget(QLabel("X"))
    pos_layout.addWidget(self.txt_x)
    pos_layout.addWidget(QLabel("Y"))
    pos_layout.addWidget(self.txt_y)
    pos_layout.addWidget(QLabel("Z"))
    pos_layout.addWidget(self.txt_z)
    pos_layout.addStretch()

    self.rb_goto_loc = QRadioButton("Goto location (machine coord.)")
    self.rb_atc = QRadioButton("Automatic Tool Changer")

    layout_tool.addWidget(self.rb_ignore_tc)
    layout_tool.addWidget(self.rb_stop_tc)
    layout_tool.addLayout(pos_layout)
    layout_tool.addWidget(self.rb_goto_loc)
    layout_tool.addWidget(self.rb_atc)
    group_tool.setLayout(layout_tool)

    # Laser options Group
    group_laser = QGroupBox("Laser options")
    layout_laser = QVBoxLayout()
    self.chk_laser = QCheckBox(
        "Gray level laser engraving (A axis controls PWM duty cycle)"
    )
    layout_laser.addWidget(self.chk_laser)
    layout_laser.addStretch()
    group_laser.setLayout(layout_laser)

    mid_layout.addWidget(group_tool, stretch=1)
    mid_layout.addWidget(group_laser, stretch=1)
    main_layout.addLayout(mid_layout)

    # 3. Bottom Grid Settings
    grid_layout = QGridLayout()

    self.chk_g04 = QCheckBox("G04 dwell time in seconds")
    self.chk_ignore_gcode = QCheckBox("Ignore unsupported G codes")
    self.chk_auto_limits = QCheckBox("Auto limits override")
    self.chk_auto_limits.setChecked(True)

    lbl_buffer = QLabel("Motion buffer size:")
    self.combo_buffer = QComboBox()
    self.combo_buffer.addItems(["Normal (default)", "Small", "Large"])

    # Maximum step frequency ComboBox (0 -> 125 kHz, 1 -> 250 kHz)
    lbl_freq = QLabel("Maximum step frequency:")
    self.combo_freq = QComboBox()
    self.combo_freq.addItem("125 kHz", 0)
    self.combo_freq.addItem("250 kHz", 1)

    self.chk_probe_limit = QCheckBox("Probe as limit")
    self.chk_dme = QCheckBox("Enable DME server")

    grid_layout.addWidget(self.chk_g04, 0, 0)
    grid_layout.addWidget(lbl_buffer, 0, 1, Qt.AlignmentFlag.AlignRight)
    grid_layout.addWidget(self.combo_buffer, 0, 2)

    grid_layout.addWidget(self.chk_ignore_gcode, 1, 0)
    grid_layout.addWidget(lbl_freq, 1, 1, Qt.AlignmentFlag.AlignRight)
    grid_layout.addWidget(self.combo_freq, 1, 2)

    grid_layout.addWidget(self.chk_auto_limits, 2, 0)
    grid_layout.addWidget(self.chk_probe_limit, 2, 2)

    grid_layout.addWidget(self.chk_dme, 3, 2)

    main_layout.addLayout(grid_layout)
    main_layout.addStretch()

  def load_settings(self):
    """Lexon cilësimet nga ConfigManager (përputhshëm me formatin tënd dhe atë të mikroCNC)."""
    if not self.config_manager:
      return

    # Lexon GCodeInit nga [GENERAL]
    gcode_init = self.config_manager.get(
        "GENERAL", "GCodeInit", fallback="G17 G64 G49 G40"
    )
    self.txt_gcode_init.setText(gcode_init)

    # Lexon MaxFreq nga [MotionController] (0=125 kHz, 1=250 kHz)
    raw_max_freq = self.config_manager.get(
        "MotionController", "MaxFreq", fallback="0"
    )
    try:
      val_freq = int(raw_max_freq)
    except ValueError:
      val_freq = 0

    idx = self.combo_freq.findData(val_freq)
    if idx != -1:
      self.combo_freq.setCurrentIndex(idx)
    else:
      self.combo_freq.setCurrentIndex(0)

    # Lexon IP-në dhe Kontrolluesin qoftë nga [GENERAL] ose [MotionController]
    raw_ip = self.config_manager.get(
        "GENERAL", "ControllerIP", fallback=None
    ) or self.config_manager.get(
        "MotionController", "IP", fallback="192.168.1.222"
    )

    ip_address = hex_to_ip(raw_ip)

    raw_type = self.config_manager.get(
        "GENERAL", "MotionController", fallback=None
    ) or self.config_manager.get("MotionController", "Type", fallback="2")

    if raw_type.isdigit():
      controller_type = REVERSE_CONTROLLER_MAP.get(int(raw_type), "ETH-MCI")
    else:
      controller_type = raw_type

  def save_settings(self):
    """Ruan cilësimet te ConfigManager."""
    if not self.config_manager:
      return

    self.config_manager.set(
        "GENERAL", "GCodeInit", self.txt_gcode_init.text()
    )

    # Ruan MaxFreq te [MotionController] (0 ose 1)
    selected_freq = self.combo_freq.currentData()
    self.config_manager.set(
        "MotionController", "MaxFreq", str(selected_freq)
    )


class AxisOutputPinsWidget(QWidget):
  """Faqja Axis output pins."""

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager
    self.init_ui()
    self.load_data()

  def init_ui(self):
    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    self.table = QTableWidget()
    self.table.setColumnCount(6)
    self.table.setHorizontalHeaderLabels([
        "Axis",
        "Enable",
        "Step Pin",
        "Dir Pin",
        "Step ActiveLow",
        "Dir ActiveLow",
    ])

    header = self.table.horizontalHeader()
    if header is not None:
      header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    self.table.verticalHeader().setVisible(False)
    self.table.setAlternatingRowColors(True)

    layout.addWidget(self.table)

    note_label = QLabel(
        "NOTE: Spindle step pin is used for PWM output in spindle PWM motor"
        " control mode"
    )
    note_label.setStyleSheet(
        "font-size: 12px; font-weight: bold; color: #a0a0a0; margin-top: 10px;"
    )
    layout.addWidget(note_label)

  def load_data(self):
    """Lexon të dhënat e akseve dhe kunjat nga skedari .ini."""
    axes_list = ["X", "Y", "Z", "A", "B", "C", "Spindle"]

    enabled_status = {}
    if self.config_manager and hasattr(
        self.config_manager, "get_axis_enable_status"
    ):
      enabled_status = self.config_manager.get_axis_enable_status()

    defaults = {
        "X": (True, 1, 2, False, False),
        "Y": (True, 3, 4, False, False),
        "Z": (True, 5, 6, False, False),
        "A": (True, 0, 0, False, False),
        "B": (False, 0, 0, False, False),
        "C": (False, 0, 0, False, False),
        "Spindle": (True, 9, 0, False, False),
    }

    self.table.setRowCount(len(axes_list))

    for row, axis_name in enumerate(axes_list):
      def_enable, def_step, def_dir, def_sal, def_dal = defaults[axis_name]

      # Lexon enable nga [AXIS_ENABLE] nëse ekziston
      if self.config_manager:
        raw_enable = self.config_manager.get(
            "AXIS_ENABLE", axis_name, fallback=str(def_enable)
        )
        is_enabled = raw_enable.lower() in ("true", "1")
      else:
        is_enabled = enabled_status.get(axis_name, def_enable)

      # Lexon StepPin, DirPin, StepActiveLow, DirActiveLow nga [AXIS_X], [AXIS_Y], etj.
      step_pin = def_step
      dir_pin = def_dir
      step_al = def_sal
      dir_al = def_dal

      if self.config_manager:
        section = f"AXIS_{axis_name}"
        step_pin = int(
            self.config_manager.get(section, "StepPin", fallback=str(def_step))
        )
        dir_pin = int(
            self.config_manager.get(section, "DirPin", fallback=str(def_dir))
        )
        step_al = (
            self.config_manager.get(
                section, "StepActiveLow", fallback=str(def_sal)
            ).lower()
            == "true"
        )
        dir_al = (
            self.config_manager.get(
                section, "DirActiveLow", fallback=str(def_dal)
            ).lower()
            == "true"
        )

      # 0. Axis Name
      item_axis = QTableWidgetItem(axis_name)
      item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
      self.table.setItem(row, 0, item_axis)

      # 1. Enable
      chk_enable = QCheckBox()
      chk_enable.setChecked(is_enabled)
      self._add_widget_centered(row, 1, chk_enable)

      # 2. Step Pin
      spin_step = QSpinBox()
      spin_step.setRange(0, 255)
      spin_step.setValue(step_pin)
      spin_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 2, spin_step)

      # 3. Dir Pin
      spin_dir = QSpinBox()
      spin_dir.setRange(0, 255)
      spin_dir.setValue(dir_pin)
      spin_dir.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 3, spin_dir)

      # 4. Step ActiveLow
      chk_step_al = QCheckBox()
      chk_step_al.setChecked(step_al)
      self._add_widget_centered(row, 4, chk_step_al)

      # 5. Dir ActiveLow
      chk_dir_al = QCheckBox()
      chk_dir_al.setChecked(dir_al)
      self._add_widget_centered(row, 5, chk_dir_al)

  def _add_widget_centered(self, row: int, col: int, widget: QWidget):
    container = QWidget()
    lay = QHBoxLayout(container)
    lay.addWidget(widget)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.setContentsMargins(0, 0, 0, 0)
    self.table.setCellWidget(row, col, container)

  def _get_checkbox_state(self, row: int, col: int) -> bool:
    container = self.table.cellWidget(row, col)
    if container is not None:
      chk = container.findChild(QCheckBox)
      if chk is not None:
        return chk.isChecked()
    return False

  def get_data(self) -> dict:
    data = {}
    axes = ["X", "Y", "Z", "A", "B", "C", "Spindle"]
    for row, axis in enumerate(axes):
      spin_step = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
      spin_dir = cast(Optional[QSpinBox], self.table.cellWidget(row, 3))

      step_val = spin_step.value() if spin_step is not None else 0
      dir_val = spin_dir.value() if spin_dir is not None else 0

      data[axis] = {
          "enable": self._get_checkbox_state(row, 1),
          "step_pin": step_val,
          "dir_pin": dir_val,
          "step_active_low": self._get_checkbox_state(row, 4),
          "dir_active_low": self._get_checkbox_state(row, 5),
      }
    return data

  def save_settings(self):
    """Ruan të gjitha të dhënat te ConfigManager në formatin tuaj MILL.ini."""
    if not self.config_manager:
      return

    data = self.get_data()

    # 1. Ruan statusin te [AXIS_ENABLE]
    for ax in ["X", "Y", "Z", "A", "B", "C"]:
      if ax in data:
        self.config_manager.set(
            "AXIS_ENABLE", ax, "True" if data[ax]["enable"] else "False"
        )

    # 2. Ruan te [AXIS_X], [AXIS_Y], etj.
    for axis, info in data.items():
      section = f"AXIS_{axis}"
      self.config_manager.set(section, "StepPin", str(info["step_pin"]))
      self.config_manager.set(section, "DirPin", str(info["dir_pin"]))
      self.config_manager.set(
          section,
          "StepActiveLow",
          "True" if info["step_active_low"] else "False",
      )
      self.config_manager.set(
          section,
          "DirActiveLow",
          "True" if info["dir_active_low"] else "False",
      )


class SetupDialog(QDialog):

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager
    self.setWindowTitle("Setup")
    self.resize(900, 600)

    self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QTreeWidget { background-color: #252526; color: #CCCCCC; border: 1px solid #333333; }
            QTreeWidget::item:selected { background-color: #007ACC; color: white; }
            QGroupBox { border: 1px solid #333333; border-radius: 4px; margin-top: 10px; font-weight: bold; color: #007ACC; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QLineEdit, QComboBox { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 3px; padding: 4px; }
            QPushButton { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #007ACC; border-color: #007ACC; }
            QCheckBox, QRadioButton, QLabel { color: #CCCCCC; }
            QTableWidget { background-color: #252526; color: #FFFFFF; gridline-color: #333333; border: 1px solid #333333; }
            QHeaderView::section { background-color: #2D2D30; color: #FFFFFF; padding: 4px; border: 1px solid #333333; }
        """)

    self.init_ui()
    self.load_settings()

  def init_ui(self):
    root_layout = QVBoxLayout(self)
    content_layout = QHBoxLayout()

    self.tree = QTreeWidget()
    self.tree.setHeaderHidden(True)
    self.tree.setFixedWidth(200)

    item_gen = QTreeWidgetItem(self.tree, ["General settings"])

    item_axis = QTreeWidgetItem(self.tree, ["Axis setup"])
    item_axis.addChildren([
        QTreeWidgetItem(["Axis output pins"]),
        QTreeWidgetItem(["Motor profiles"]),
        QTreeWidgetItem(["Homing/Limits"]),
        QTreeWidgetItem(["Slave axis"]),
        QTreeWidgetItem(["Backlash compens."]),
        QTreeWidgetItem(["Eth-mc advanced"]),
    ])
    item_axis.setExpanded(True)

    self.tree.addTopLevelItem(QTreeWidgetItem(["Input signals"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["Output signals"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["Encoders & MPGs"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["Motion planner"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["Spindle & Coolant"]))

    item_thc = QTreeWidgetItem(self.tree, ["THC setup"])
    item_thc.addChildren(
        [QTreeWidgetItem(["General THC"]), QTreeWidgetItem(["Internal THC"])]
    )
    item_thc.setExpanded(True)

    self.tree.addTopLevelItem(QTreeWidgetItem(["Button scripts"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["External buttons"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["Persist options"]))
    self.tree.addTopLevelItem(QTreeWidgetItem(["UI options"]))

    content_layout.addWidget(self.tree)

    self.stacked_widget = QStackedWidget()

    self.general_page = GeneralSettingsWidget(self.config_manager)
    self.stacked_widget.addWidget(self.general_page)

    self.axis_pins_page = AxisOutputPinsWidget(self.config_manager)
    self.axis_pins_page.setStyleSheet("""
            QCheckBox { color: #FFFFFF; }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #888888; border-radius: 3px;
                background-color: #252526;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #FFFFFF; background-color: #3E3E42;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC; border: 2px solid #007ACC;
            }
        """)

    self.stacked_widget.addWidget(self.axis_pins_page)

    self.placeholder_page = QWidget()
    ph_layout = QVBoxLayout(self.placeholder_page)
    self.lbl_placeholder = QLabel(
        "Konfigurimi për këtë seksion do të shtohet së shpejti."
    )
    self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ph_layout.addWidget(self.lbl_placeholder)

    self.stacked_widget.addWidget(self.placeholder_page)

    content_layout.addWidget(self.stacked_widget, stretch=1)
    root_layout.addLayout(content_layout)

    bottom_layout = QHBoxLayout()
    btn_import = QPushButton("Import from profile...")
    btn_ok = QPushButton("OK")
    btn_cancel = QPushButton("Cancel")

    btn_ok.clicked.connect(self.accept)
    btn_cancel.clicked.connect(self.reject)

    bottom_layout.addWidget(btn_import)
    bottom_layout.addStretch()
    bottom_layout.addWidget(btn_ok)
    bottom_layout.addWidget(btn_cancel)

    root_layout.addLayout(bottom_layout)

    self.tree.currentItemChanged.connect(self.on_tree_selection_changed)
    self.tree.setCurrentItem(item_gen)

  def load_settings(self):
    pass

  def on_tree_selection_changed(self, current, previous):
    if not current:
      return

    if current.childCount() > 0:
      current.setExpanded(True)
      first_child = current.child(0)
      self.tree.setCurrentItem(first_child)
      return

    text = current.text(0)
    if text == "General settings":
      self.stacked_widget.setCurrentIndex(0)
    elif text == "Axis output pins":
      self.stacked_widget.setCurrentIndex(1)
    else:
      self.lbl_placeholder.setText(
          f"Seksioni: [{text}] - Në proces zhvillimi"
      )
      self.stacked_widget.setCurrentIndex(2)

  def accept(self):
    self.general_page.save_settings()
    self.axis_pins_page.save_settings()

    if self.config_manager and hasattr(self.config_manager, "save_config"):
      self.config_manager.save_config()

    super().accept()