from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PersistOptionsWidget(QWidget):
    """Faqja Persist options për ruajtjen e gjendjes së funksioneve pas mbylljes së aplikacionit."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.functions_list = [
            "Feedrate",
            "Spindle speed",
            "Selected tool",
            "Jog mode",
        ]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([
            "Function",
            "Remember setting",
        ])

        self.table.setRowCount(len(self.functions_list))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

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
        for row, func_name in enumerate(self.functions_list):
            section = f"PERSIST_{func_name.replace(' ', '_')}"
            is_enabled = False

            if self.config_manager:
                is_enabled = self.config_manager.get_boolean(section, "Remember", False)

            # 0. Function name
            item_name = QTableWidgetItem(func_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            # 1. Remember setting Checkbox
            self._add_checkbox_centered(row, 1, is_enabled)

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

        for row, func_name in enumerate(self.functions_list):
            section = f"PERSIST_{func_name.replace(' ', '_')}"
            remember = self._get_checkbox_state(row, 1)

            self.config_manager.set(section, "Remember", str(remember))