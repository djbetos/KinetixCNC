from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SlaveAxisWidget(QWidget):
    """Faqja Slave axis për sinkronizimin e akseve dvojëze (Master/Slave)."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.master_axes = ["X", "Y", "Z"]
        self.combo_slaves = {}

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 1. GroupBox për konfigurimin Master / Slave
        group_slave = QGroupBox()
        grid = QGridLayout(group_slave)
        grid.setSpacing(12)
        grid.setContentsMargins(20, 20, 20, 20)

        # Titujt e kolonave
        lbl_master_hdr = QLabel("Master")
        lbl_master_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #CCCCCC;")
        lbl_slave_hdr = QLabel("Slave")
        lbl_slave_hdr.setStyleSheet("font-weight: bold; font-size: 13px; color: #CCCCCC;")

        grid.addWidget(lbl_master_hdr, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(lbl_slave_hdr, 0, 1, Qt.AlignmentFlag.AlignCenter)

        # Rreshtat për X, Y, Z
        for row, master_ax in enumerate(self.master_axes, start=1):
            lbl_ax = QLabel(f"{master_ax}:")
            lbl_ax.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")

            combo = QComboBox()
            combo.setFixedWidth(130)
            combo.addItem("None")

            # Opcionet e mundshme për aksin Slave (A, B, C)
            possible_slaves = ["A", "B", "C"]
            for s_ax in possible_slaves:
                if s_ax != master_ax:
                    combo.addItem(s_ax)

            grid.addWidget(lbl_ax, row, 0, Qt.AlignmentFlag.AlignRight)
            grid.addWidget(combo, row, 1, Qt.AlignmentFlag.AlignLeft)
            self.combo_slaves[master_ax] = combo

        # Qendërsimi i GroupBox
        center_h = QHBoxLayout()
        center_h.addStretch()
        center_h.addWidget(group_slave)
        center_h.addStretch()
        main_layout.addLayout(center_h)

        # 2. Checkbox: Home slave with master
        self.chk_home_slave = QCheckBox("Home slave with master")
        self.chk_home_slave.setStyleSheet("font-size: 12px; color: #CCCCCC;")

        center_chk = QHBoxLayout()
        center_chk.addStretch()
        center_chk.addWidget(self.chk_home_slave)
        center_chk.addStretch()

        main_layout.addLayout(center_chk)
        main_layout.addStretch()

    def load_data(self):
        if not self.config_manager:
            return

        for master_ax in self.master_axes:
            section = f"SLAVE_{master_ax}"
            slave_val = self.config_manager.get(section, "SlaveAxis", fallback="None")
            combo = self.combo_slaves[master_ax]
            idx = combo.findText(slave_val)
            if idx != -1:
                combo.setCurrentIndex(idx)
            else:
                combo.setCurrentIndex(0)

        home_slave = self.config_manager.get_boolean("HOMING", "HomeSlaveWithMaster", False)
        self.chk_home_slave.setChecked(home_slave)

    def save_settings(self):
        if not self.config_manager:
            return

        for master_ax in self.master_axes:
            section = f"SLAVE_{master_ax}"
            selected_slave = self.combo_slaves[master_ax].currentText()
            self.config_manager.set(section, "SlaveAxis", selected_slave)

        self.config_manager.set(
            "HOMING", "HomeSlaveWithMaster", str(self.chk_home_slave.isChecked())
        )