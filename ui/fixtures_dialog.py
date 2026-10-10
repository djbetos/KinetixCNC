from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class FixturesDialog(QDialog):
    """Dritarja Fixtures për menaxhimin e offset-eve të koorodinatave të punës (G54 - G59, etj.)."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Fixtures")
        self.resize(750, 450)

        self.fixture_names = [
            "1. (G54)", "2. (G55)", "3. (G56)", "4. (G57)", "5. (G58)", "6. (G59)",
            "7. (G54.1 p07)", "8. (G54.1 p08)", "9. (G54.1 p09)", "10. (G54.1 p10)",
            "11. (G54.1 p11)", "12. (G54.1 p12)", "13. (G54.1 p13)", "14. (G54.1 p14)",
            "15. (G54.1 p15)", "16. (G54.1 p16)", "17. (G54.1 p17)", "18. (G54.1 p18)",
            "19. (G54.1 p19)", "20. (G54.1 p20)"
        ]
        self.axes = ["X", "Y", "Z", "A", "B", "C"]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Tabela e Fixtures
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.axes) + 1)
        headers = ["Fixture"] + [f"{ax} offset" for ax in self.axes]
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(self.fixture_names))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            for i in range(1, len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 120)
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
        defaults = {
            "1. (G54)": {"X": -250.0, "Y": -30.0, "Z": 90.0, "A": 0.0, "B": 0.0, "C": 0.0},
        }

        for row, fix_name in enumerate(self.fixture_names):
            item_name = QTableWidgetItem(fix_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            def_vals = defaults.get(fix_name, {ax: 0.0 for ax in self.axes})

            for col, ax in enumerate(self.axes, start=1):
                val = def_vals.get(ax, 0.0)
                if self.config_manager:
                    section = f"FIXTURE_{row + 1}"
                    val = float(self.config_manager.get(section, f"{ax}_offset", str(val)))

                spin = QDoubleSpinBox()
                spin.setRange(-100000.0, 100000.0)
                spin.setDecimals(4)
                spin.setValue(val)
                spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, col, spin)

    def accept(self):
        if self.config_manager:
            for row, fix_name in enumerate(self.fixture_names):
                section = f"FIXTURE_{row + 1}"
                for col, ax in enumerate(self.axes, start=1):
                    spin = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, col))
                    val = spin.value() if spin is not None else 0.0
                    self.config_manager.set(section, f"{ax}_offset", f"{val:.4f}")
        super().accept()