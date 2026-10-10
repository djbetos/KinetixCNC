from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class EncodersMPGsWidget(QWidget):
  """Faqja Encoders & MPGs me dizajn uniform me treguesit e tjerë."""

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager

    self.items_list = ["MPG1", "MPG2", "MPG3", "ENC1", "ENC2", "ENC3", "ENC4"]

    self.init_ui()
    self.load_data()

  def init_ui(self):
    layout = QVBoxLayout(self)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    self.table = QTableWidget()
    self.table.setColumnCount(6)
    self.table.setHorizontalHeaderLabels([
        "Input",
        "Enable",
        "A pin",
        "B pin",
        "Debounce [x100uS]",
        "Step [mm]",
    ])

    self.table.setRowCount(len(self.items_list))
    self.table.verticalHeader().setVisible(False)
    self.table.setAlternatingRowColors(True)

    header = self.table.horizontalHeader()
    if header is not None:
      header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
      header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
      header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

    self.table.setColumnWidth(0, 110)  # Input
    self.table.setColumnWidth(1, 65)  # Enable
    self.table.setColumnWidth(2, 80)  # A pin
    self.table.setColumnWidth(3, 80)  # B pin

    layout.addWidget(self.table)

    note_label = QLabel(
        "NOTE: reading of maximum two encoders is supported so if more is"
        " selected then only first two enabled encoders are used"
    )
    note_label.setStyleSheet(
        "font-size: 11px; font-weight: bold; color: #a0a0a0; margin-top: 5px;"
    )
    note_label.setWordWrap(True)
    layout.addWidget(note_label)

  def _add_checkbox_centered(
      self, row: int, col: int, checked: bool
  ) -> QCheckBox:
    chk = QCheckBox()
    chk.setChecked(checked)
    container = QWidget()
    lay = QHBoxLayout(container)
    lay.addWidget(chk)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.setContentsMargins(0, 0, 0, 0)
    self.table.setCellWidget(row, col, container)
    return chk

  def load_data(self):
    for row, item_name in enumerate(self.items_list):
      # 0. Input Name
      item_widget = QTableWidgetItem(item_name)
      item_widget.setFlags(Qt.ItemFlag.ItemIsEnabled)
      item_widget.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setItem(row, 0, item_widget)

      section = f"ENCODER_{item_name}"
      is_enabled = False
      a_pin = 0
      b_pin = 0
      debounce = 0
      step_mm = 0.2500

      if self.config_manager:
        is_enabled = self.config_manager.get_boolean(section, "Enable", False)
        a_pin = int(self.config_manager.get(section, "APin", "0"))
        b_pin = int(self.config_manager.get(section, "BPin", "0"))
        debounce = int(self.config_manager.get(section, "Debounce", "0"))
        step_mm = float(self.config_manager.get(section, "Step", "0.2500"))

      # 1. Enable QCheckBox
      self._add_checkbox_centered(row, 1, is_enabled)

      # 2. A pin SpinBox
      spin_a = QSpinBox()
      spin_a.setRange(0, 255)
      spin_a.setValue(a_pin)
      spin_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 2, spin_a)

      # 3. B pin SpinBox
      spin_b = QSpinBox()
      spin_b.setRange(0, 255)
      spin_b.setValue(b_pin)
      spin_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 3, spin_b)

      # 4. Debounce SpinBox
      spin_deb = QSpinBox()
      spin_deb.setRange(0, 10000)
      spin_deb.setValue(debounce)
      spin_deb.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 4, spin_deb)

      # 5. Step DoubleSpinBox
      spin_step = QDoubleSpinBox()
      spin_step.setRange(0.0001, 100.0)
      spin_step.setDecimals(4)
      spin_step.setSingleStep(0.01)
      spin_step.setValue(step_mm)
      spin_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 5, spin_step)

  def _get_checkbox_state(self, row: int, col: int) -> bool:
    container = self.table.cellWidget(row, col)
    if container is not None:
      chk = container.findChild(QCheckBox)
      if chk is not None:
        return chk.isChecked()
    return False

  def save_settings(self):
    if not self.config_manager:
      return

    for row, item_name in enumerate(self.items_list):
      section = f"ENCODER_{item_name}"

      enabled = self._get_checkbox_state(row, 1)

      spin_a = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
      spin_b = cast(Optional[QSpinBox], self.table.cellWidget(row, 3))
      spin_deb = cast(Optional[QSpinBox], self.table.cellWidget(row, 4))
      spin_step = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, 5))

      a_pin = spin_a.value() if spin_a is not None else 0
      b_pin = spin_b.value() if spin_b is not None else 0
      debounce = spin_deb.value() if spin_deb is not None else 0
      step_mm = spin_step.value() if spin_step is not None else 0.2500

      self.config_manager.set(section, "Enable", str(enabled))
      self.config_manager.set(section, "APin", str(a_pin))
      self.config_manager.set(section, "BPin", str(b_pin))
      self.config_manager.set(section, "Debounce", str(debounce))
      self.config_manager.set(section, "Step", f"{step_mm:.4f}")