from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class OutputSignalsWidget(QWidget):
  """Faqja Output signals me dizajnin e përputhur me Input signals."""

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager

    # Lista e plotë e Output Signals nga mikroCNC
    self.output_signals = [
        "EXT1",
        "EXT2",
        "EXT3",
        "EXT4",
        "EXT5",
        "EXT6",
        "Enable",
        "Charge pump 1",
        "Charge pump 2",
    ]

    # Shtimi i 16 Output-eve të përdoruesit (OUTPUT1 deri OUTPUT16)
    for i in range(1, 17):
      self.output_signals.append(f"OUTPUT{i}")

    self.init_ui()
    self.load_data()

  def init_ui(self):
    layout = QVBoxLayout(self)
    layout.setContentsMargins(10, 10, 10, 10)

    self.table = QTableWidget()
    self.table.setColumnCount(4)
    self.table.setHorizontalHeaderLabels(
        ["Output Signal", "Enable", "Pin", "Active Low"]
    )

    self.table.setRowCount(len(self.output_signals))
    self.table.verticalHeader().setVisible(False)
    self.table.setAlternatingRowColors(True)

    header = self.table.horizontalHeader()
    if header is not None:
      header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
      header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    # Rregullimi i gjerësive të kolonave sipas specifikimeve
    self.table.setColumnWidth(0, 140)  # Output Signal
    self.table.setColumnWidth(1, 75)  # Enable
    self.table.setColumnWidth(2, 110)  # Pin

    layout.addWidget(self.table)

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
    for row, sig_name in enumerate(self.output_signals):
      # 0. Output Signal Name
      item_name = QTableWidgetItem(sig_name)
      item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
      item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setItem(row, 0, item_name)

      section = f"OUTPUT_SIGNAL_{sig_name}"
      is_enabled = False
      pin_num = 0
      active_low = False

      if self.config_manager:
        is_enabled = self.config_manager.get_boolean(section, "Enable", False)
        pin_num = int(self.config_manager.get(section, "Pin", "0"))
        active_low = self.config_manager.get_boolean(
            section, "ActiveLow", False
        )

      # Vlera default për 'Enable' (Pin 24)
      if (
          sig_name == "Enable"
          and self.config_manager
          and not self.config_manager.config.has_section(section)
      ):
        is_enabled = True
        pin_num = 24
        active_low = False

      # 1. Enable QCheckBox
      self._add_checkbox_centered(row, 1, is_enabled)

      # 2. Pin SpinBox
      spin_pin = QSpinBox()
      spin_pin.setRange(0, 255)
      spin_pin.setValue(pin_num)
      spin_pin.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 2, spin_pin)

      # 3. Active Low QCheckBox
      self._add_checkbox_centered(row, 3, active_low)

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

    for row, sig_name in enumerate(self.output_signals):
      section = f"OUTPUT_SIGNAL_{sig_name}"

      enabled = self._get_checkbox_state(row, 1)
      active_low = self._get_checkbox_state(row, 3)
      spin_pin = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
      pin_num = spin_pin.value() if spin_pin is not None else 0

      self.config_manager.set(section, "Enable", str(enabled))
      self.config_manager.set(section, "Pin", str(pin_num))
      self.config_manager.set(section, "ActiveLow", str(active_low))