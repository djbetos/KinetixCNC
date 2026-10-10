from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HomingLimitsWidget(QWidget):
    """Faqja Homing/Limits me dizajnin e përputhur me pjesët e tjera."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.axes_list = ["X", "Y", "Z", "A", "B", "C"]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # 1. Tabela Homing/Limits
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Axis",
            "Home neg",
            "Auto zero",
            "Offset",
            "Speed [%]",
            "Soft min",
            "Soft max",
        ])

        self.table.setRowCount(len(self.axes_list))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 50)   # Axis
        self.table.setColumnWidth(1, 80)   # Home neg
        self.table.setColumnWidth(2, 80)   # Auto zero

        main_layout.addWidget(self.table)

        # 2. Seksioni i Poshtëm: G28 Location dhe Retract Speed
        bottom_layout = QHBoxLayout()

        # GroupBox për G28 home location
        group_g28 = QGroupBox("G28 home location")
        grid_g28 = QGridLayout()

        self.txt_g28 = {}
        for idx, ax in enumerate(self.axes_list):
            row = idx % 3
            col_lbl = (idx // 3) * 2
            col_txt = col_lbl + 1

            lbl = QLabel(f"{ax}:")
            txt = QLineEdit("0")
            txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt.setFixedWidth(80)

            grid_g28.addWidget(lbl, row, col_lbl)
            grid_g28.addWidget(txt, row, col_txt)
            self.txt_g28[ax] = txt

        group_g28.setLayout(grid_g28)
        bottom_layout.addWidget(group_g28)

        # Retract Speed & Dereference Option
        v_right = QVBoxLayout()
        v_right.setSpacing(10)

        v_retract = QVBoxLayout()
        lbl_retract = QLabel("Home retract speed [%]:")
        self.txt_retract_speed = QLineEdit("10")
        self.txt_retract_speed.setFixedWidth(80)
        v_retract.addWidget(lbl_retract)
        v_retract.addWidget(self.txt_retract_speed)

        self.chk_deref = QCheckBox("Dereference all axes on disconnect")

        v_right.addLayout(v_retract)
        v_right.addWidget(self.chk_deref)
        v_right.addStretch()

        bottom_layout.addLayout(v_right)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

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
        defaults = {
            "X": (False, True, 0.0, 10.0, -100.0, 100.0),
            "Y": (False, True, 0.0, 10.0, -100.0, 100.0),
            "Z": (False, True, 0.0, 10.0, -100.0, 100.0),
            "A": (False, True, 0.0, 10.0, -100.0, 100.0),
            "B": (False, True, 0.0, 10.0, -100.0, 100.0),
            "C": (False, True, 0.0, 10.0, -100.0, 100.0),
        }

        for row, ax in enumerate(self.axes_list):
            def_neg, def_az, def_off, def_spd, def_smin, def_smax = defaults[ax]

            section = f"HOMING_{ax}"
            home_neg = def_neg
            auto_zero = def_az
            offset = def_off
            speed = def_spd
            soft_min = def_smin
            soft_max = def_smax

            if self.config_manager:
                home_neg = self.config_manager.get_boolean(section, "HomeNeg", def_neg)
                auto_zero = self.config_manager.get_boolean(section, "AutoZero", def_az)
                offset = float(self.config_manager.get(section, "Offset", str(def_off)))
                speed = float(self.config_manager.get(section, "Speed", str(def_spd)))
                soft_min = float(self.config_manager.get(section, "SoftMin", str(def_smin)))
                soft_max = float(self.config_manager.get(section, "SoftMax", str(def_smax)))

            # 0. Axis
            item_axis = QTableWidgetItem(ax)
            item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_axis)

            # 1. Home neg
            self._add_checkbox_centered(row, 1, home_neg)

            # 2. Auto zero
            self._add_checkbox_centered(row, 2, auto_zero)

            # 3. Offset
            spin_off = QDoubleSpinBox()
            spin_off.setRange(-10000.0, 10000.0)
            spin_off.setDecimals(4)
            spin_off.setValue(offset)
            spin_off.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 3, spin_off)

            # 4. Speed [%]
            spin_spd = QDoubleSpinBox()
            spin_spd.setRange(0.0001, 100.0)
            spin_spd.setDecimals(4)
            spin_spd.setValue(speed)
            spin_spd.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 4, spin_spd)

            # 5. Soft min
            spin_smin = QDoubleSpinBox()
            spin_smin.setRange(-100000.0, 100000.0)
            spin_smin.setDecimals(4)
            spin_smin.setValue(soft_min)
            spin_smin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 5, spin_smin)

            # 6. Soft max
            spin_smax = QDoubleSpinBox()
            spin_smax.setRange(-100000.0, 100000.0)
            spin_smax.setDecimals(4)
            spin_smax.setValue(soft_max)
            spin_smax.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 6, spin_smax)

        # Leximi i G28 / Retract speed / Deref
        if self.config_manager:
            for ax in self.axes_list:
                val = self.config_manager.get("G28", ax, fallback="0")
                self.txt_g28[ax].setText(val)

            ret_speed = self.config_manager.get("HOMING", "HomeRetractSpeed", fallback="10")
            self.txt_retract_speed.setText(ret_speed)

            deref = self.config_manager.get_boolean("HOMING", "DereferenceOnDisconnect", False)
            self.chk_deref.setChecked(deref)

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

        for row, ax in enumerate(self.axes_list):
            section = f"HOMING_{ax}"

            home_neg = self._get_checkbox_state(row, 1)
            auto_zero = self._get_checkbox_state(row, 2)

            spin_off = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, 3))
            spin_spd = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, 4))
            spin_smin = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, 5))
            spin_smax = cast(Optional[QDoubleSpinBox], self.table.cellWidget(row, 6))

            offset = spin_off.value() if spin_off is not None else 0.0
            speed = spin_spd.value() if spin_spd is not None else 10.0
            soft_min = spin_smin.value() if spin_smin is not None else -100.0
            soft_max = spin_smax.value() if spin_smax is not None else 100.0

            self.config_manager.set(section, "HomeNeg", str(home_neg))
            self.config_manager.set(section, "AutoZero", str(auto_zero))
            self.config_manager.set(section, "Offset", f"{offset:.4f}")
            self.config_manager.set(section, "Speed", f"{speed:.4f}")
            self.config_manager.set(section, "SoftMin", f"{soft_min:.4f}")
            self.config_manager.set(section, "SoftMax", f"{soft_max:.4f}")

        # Ruajtja e G28 / Retract speed / Deref
        for ax in self.axes_list:
            self.config_manager.set("G28", ax, self.txt_g28[ax].text())

        self.config_manager.set("HOMING", "HomeRetractSpeed", self.txt_retract_speed.text())
        self.config_manager.set("HOMING", "DereferenceOnDisconnect", str(self.chk_deref.isChecked()))