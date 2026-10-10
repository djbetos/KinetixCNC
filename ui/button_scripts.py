from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ButtonScriptsWidget(QWidget):
    """Faqja Button scripts për lidhjen e funksioneve me skriptet e përdoruesit."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        # Lista e funksioneve dhe skripteve implicite sipas ndërfaqes
        self.scripts_data = [
            ("RefAllHome", "RefAllHome"),
            ("AutoToolZero", "AutoToolZero"),
            ("M30 calls script", "M1030"),
            ("Background task", "BkgTask"),
            ("GotoZero", "GotoZero"),
            ("Start", "OnStart"),
            ("Stop", "OnStop"),
            ("Feedhold", "OnFeedhold"),
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
            "User script file",
        ])

        self.table.setRowCount(len(self.scripts_data))
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
        for row, (func_name, default_script) in enumerate(self.scripts_data):
            section = f"SCRIPT_{func_name.replace(' ', '_')}"
            is_enabled = False
            script_file = default_script

            if self.config_manager:
                is_enabled = self.config_manager.get_boolean(section, "Enable", False)
                script_file = self.config_manager.get(section, "ScriptFile", default_script)

            # 0. Button / function name
            item_name = QTableWidgetItem(func_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            # 1. Enable Checkbox
            self._add_checkbox_centered(row, 1, is_enabled)

            # 2. User script file LineEdit
            txt_script = QLineEdit(script_file)
            self.table.setCellWidget(row, 2, txt_script)

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

        for row, (func_name, _) in enumerate(self.scripts_data):
            section = f"SCRIPT_{func_name.replace(' ', '_')}"
            enabled = self._get_checkbox_state(row, 1)
            
            txt_widget = cast(Optional[QLineEdit], self.table.cellWidget(row, 2))
            script_file = txt_widget.text() if txt_widget is not None else ""

            self.config_manager.set(section, "Enable", str(enabled))
            self.config_manager.set(section, "ScriptFile", script_file)