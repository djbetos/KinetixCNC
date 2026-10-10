from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class ToolTableDialog(QDialog):
    """Dritarja Tooltable për menaxhimin e mjeteve, offset-eve dhe diametrave të tyre."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Tool offsets table")
        self.resize(750, 480)

        self.columns = ["No", "Tool info", "X offset", "Y offset", "Z offset", "Diameter"]
        self.num_tools = 50  # Nga 0 deri në 49

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Tabela e Mjeteve
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setRowCount(self.num_tools)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            for i in range(2, len(self.columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 70)
        main_layout.addWidget(self.table)

        # Butonat OK / Cancel në fund
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setFixedWidth(90)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

    def load_data(self):
        for row in range(self.num_tools):
            # 0. Numri i mjetit (No)
            item_no = QTableWidgetItem(str(row))
            item_no.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_no)

            # Vlerat implicite
            default_info = "Reference tool" if row == 0 else "Info"
            
            info_val = default_info
            x_val = 0.0
            y_val = 0.0
            z_val = 0.0
            d_val = 0.0

            if self.config_manager:
                info_val = self.config_manager.get_tool_param(row, "Info", default_info)
                try:
                    x_val = float(self.config_manager.get_tool_param(row, "X_offset", "0.0"))
                    y_val = float(self.config_manager.get_tool_param(row, "Y_offset", "0.0"))
                    z_val = float(self.config_manager.get_tool_param(row, "Z_offset", "0.0"))
                    d_val = float(self.config_manager.get_tool_param(row, "Diameter", "0.0"))
                except ValueError:
                    pass

            # 1. Tool info (QLineEdit)
            txt_info = QLineEdit(info_val)
            self.table.setCellWidget(row, 1, txt_info)

            # 2, 3, 4, 5. Offset-et dhe Diametri (QDoubleSpinBox)
            for col, param_key in enumerate(["X_offset", "Y_offset", "Z_offset", "Diameter"], start=2):
                spin = QDoubleSpinBox()
                spin.setRange(-100000.0, 100000.0)
                spin.setDecimals(4)
                
                val = x_val if col == 2 else (y_val if col == 3 else (z_val if col == 4 else d_val))
                spin.setValue(val)
                spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, col, spin)

    def accept(self):
        if self.config_manager:
            for row in range(self.num_tools):
                # Lexo Tool Info
                txt_widget = cast(Optional[QLineEdit], self.table.cellWidget(row, 1))
                info_text = txt_widget.text() if txt_widget is not None else ""
                self.config_manager.set_tool_param(row, "Info", info_text)

                # Lexo Offset-et dhe Diametrin
                params = ["X_offset", "Y_offset", "Z_offset", "Diameter"]
                for col, param_key in enumerate(params, start=2):
                    spin = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, col))
                    val = spin.value() if spin is not None else 0.0
                    self.config_manager.set_tool_param(row, param_key, f"{val:.4f}")

        super().accept()