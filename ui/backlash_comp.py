from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BacklashCompWidget(QWidget):
  """Faqja Backlash compensation për kompensimin e lojës mekanike në akse."""

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager
    self.axes_list = ["X", "Y", "Z", "A", "B", "C"]

    self.init_ui()
    self.load_data()

  def init_ui(self):
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(15, 15, 15, 15)
    main_layout.setSpacing(15)

    # 1. Enable Backlash Compensation Checkbox
    self.chk_enable = QCheckBox("Enable backlash compensation")
    self.chk_enable.setStyleSheet(
        "font-weight: bold; font-size: 12px; color: #CCCCCC;"
    )
    main_layout.addWidget(self.chk_enable)

    # 2. Pjesa Qendrore: Tabela dhe Shpejtësia (Side by Side)
    mid_layout = QHBoxLayout()
    mid_layout.setSpacing(25)

    # Tabela e Akseve dhe Vlerave të Backlash-it
    self.table = QTableWidget()
    self.table.setColumnCount(2)
    self.table.setHorizontalHeaderLabels(["Axis", "Backlash"])
    self.table.setRowCount(len(self.axes_list))
    self.table.verticalHeader().setVisible(False)
    self.table.setAlternatingRowColors(True)

    header = self.table.horizontalHeader()
    if header is not None:
      header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
      header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    self.table.setColumnWidth(0, 70)
    self.table.setFixedWidth(220)

    mid_layout.addWidget(self.table)

    # Pjesa e djathtë: Backlash move speed
    right_v = QVBoxLayout()
    lbl_speed = QLabel("Backlash move speed, % of max:")
    lbl_speed.setStyleSheet("color: #CCCCCC;")

    self.spin_speed = QSpinBox()
    self.spin_speed.setRange(1, 100)
    self.spin_speed.setValue(30)
    self.spin_speed.setFixedWidth(90)
    self.spin_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)

    right_v.addWidget(lbl_speed)
    right_v.addWidget(self.spin_speed)
    right_v.addStretch()

    mid_layout.addLayout(right_v)
    mid_layout.addStretch()

    main_layout.addLayout(mid_layout)

    # 3. Shënimi Informativ në fund
    note_label = QLabel(
        "NOTE: Backlash compensation is supported only by ETH-MC and ETH-MCI"
        " motion controllers"
    )
    note_label.setStyleSheet(
        "font-size: 11px; font-weight: bold; color: #A0A0A0; margin-top: 20px;"
    )
    note_label.setWordWrap(True)
    main_layout.addWidget(note_label)

    main_layout.addStretch()

  def load_data(self):
    is_enabled = False
    speed = 30

    if self.config_manager:
      is_enabled = self.config_manager.get_boolean(
          "BACKLASH", "Enable", False
      )
      speed = int(self.config_manager.get("BACKLASH", "SpeedPct", "30"))

    self.chk_enable.setChecked(is_enabled)
    self.spin_speed.setValue(speed)

    for row, ax in enumerate(self.axes_list):
      val = 0.0
      if self.config_manager:
        sec = f"AXIS_{ax}"
        val = float(self.config_manager.get(sec, "Backlash", "0.0000"))

      # 0. Axis Name
      item_axis = QTableWidgetItem(ax)
      item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
      item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setItem(row, 0, item_axis)

      # 1. Backlash DoubleSpinBox
      spin_val = QDoubleSpinBox()
      spin_val.setRange(0.0, 100.0)
      spin_val.setDecimals(4)
      spin_val.setSingleStep(0.001)
      spin_val.setValue(val)
      spin_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.table.setCellWidget(row, 1, spin_val)

  def save_settings(self):
    if not self.config_manager:
      return

    self.config_manager.set(
        "BACKLASH", "Enable", str(self.chk_enable.isChecked())
    )
    self.config_manager.set(
        "BACKLASH", "SpeedPct", str(self.spin_speed.value())
    )

    for row, ax in enumerate(self.axes_list):
      sec = f"AXIS_{ax}"
      spin_val = cast(
          Optional[QDoubleSpinBox], self.table.cellWidget(row, 1)
      )
      val = spin_val.value() if spin_val is not None else 0.0
      self.config_manager.set(sec, "Backlash", f"{val:.4f}")