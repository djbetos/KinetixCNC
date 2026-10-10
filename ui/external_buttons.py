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


class ExternalButtonsWidget(QWidget):
    """Faqja External buttons për konfigurimin e butona fizike të kontrolluesit CNC."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        # Lista e funksioneve të butona fizike sipas ndërfaqes
        self.buttons_list = [
            "Start",
            "Stop",
            "Start/Stop",
            "Start/Pause",
            "Feedhold",
            "Enable/Disable",
            "RefAllHome",
            "Spindle On/Off",
            "SoftLimits On/Off",
            "AutoToolZero",
            "JogMode cycle",
            "JogStep cycle",
            "MPG axis cycle",
            "JogX+",
            "JogX-",
            "JogY+",
            "JogY-",
            "JogZ+",
            "JogZ-",
            "JogA+",
            "JogA-",
            "Error (EStop)",
        ]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Button / function",
            "Enable",
            "INPUT#(1-10)",
        ])

        self.table.setRowCount(len(self.buttons_list))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(1, 90)

        main_layout.addWidget(self.table)
        main_layout.addStretch()

    def _add_checkbox_centered(self, row: int, col: int, checked: bool) -> QCheckBox:
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
        for row, btn_name in enumerate(self.buttons_list):
            section = f"EXT_BTN_{btn_name.replace(' ', '_').replace('(', '').replace(')', '').replace('+', 'POS').replace('-', 'NEG').replace('/', '_')}"
            is_enabled = False
            input_num = 0

            if self.config_manager:
                is_enabled = self.config_manager.get_boolean(section, "Enable", False)
                input_num = int(self.config_manager.get(section, "InputPin", "0"))

            # 0. Button / function name
            item_name = QTableWidgetItem(btn_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            # 1. Enable Checkbox
            self._add_checkbox_centered(row, 1, is_enabled)

            # 2. Input SpinBox
            spin_input = QSpinBox()
            spin_input.setRange(0, 10)
            spin_input.setValue(input_num)
            spin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 2, spin_input)

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

        for row, btn_name in enumerate(self.buttons_list):
            section = f"EXT_BTN_{btn_name.replace(' ', '_').replace('(', '').replace(')', '').replace('+', 'POS').replace('-', 'NEG').replace('/', '_')}"
            enabled = self._get_checkbox_state(row, 1)

            spin_widget = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
            input_num = spin_widget.value() if spin_widget is not None else 0

            self.config_manager.set(section, "Enable", str(enabled))
            self.config_manager.set(section, "InputPin", str(input_num))