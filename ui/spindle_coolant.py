from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SpindleCoolantWidget(QWidget):
    """Faqja Spindle & Coolant për kontrollin e frezës dhe relave të ftohjes."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.relay_signals = ["M3 (CW)", "M4 (CCW)", "M7 (Mist)", "M8 (Flood)"]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(15)

        # 1. Pjesa e Sipërme: Motor Control & PWM Settings
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # Spindle motor control Radio Group
        group_control = QGroupBox("Spindle motor control")
        v_radio = QVBoxLayout(group_control)

        self.rb_none = QRadioButton("None")
        self.rb_step_dir = QRadioButton("Step & Dir")
        self.rb_pwm = QRadioButton("PWM out")
        self.rb_none.setChecked(True)

        v_radio.addWidget(self.rb_none)
        v_radio.addWidget(self.rb_step_dir)
        v_radio.addWidget(self.rb_pwm)

        top_layout.addWidget(group_control)

        # Grid i parametrave të shpejtësisë/PWM
        grid_params = QGridLayout()
        grid_params.setHorizontalSpacing(15)
        grid_params.setVerticalSpacing(8)

        lbl_pwm_freq = QLabel("PWM frequency [Hz]")
        self.txt_pwm_freq = QLineEdit("10000")
        self.txt_pwm_freq.setFixedWidth(80)

        lbl_min_rpm = QLabel("Min spindle rpm")
        self.txt_min_rpm = QLineEdit("0")
        self.txt_min_rpm.setFixedWidth(80)

        lbl_max_rpm = QLabel("Max spindle rpm")
        self.txt_max_rpm = QLineEdit("8000")
        self.txt_max_rpm.setFixedWidth(80)

        lbl_min_duty = QLabel("Min PWM duty [%]")
        self.txt_min_duty = QLineEdit("0")
        self.txt_min_duty.setFixedWidth(80)

        lbl_max_duty = QLabel("Max PWM duty [%]")
        self.txt_max_duty = QLineEdit("100")
        self.txt_max_duty.setFixedWidth(80)

        grid_params.addWidget(lbl_pwm_freq, 0, 0)
        grid_params.addWidget(self.txt_pwm_freq, 1, 0)

        grid_params.addWidget(lbl_min_rpm, 0, 1)
        grid_params.addWidget(self.txt_min_rpm, 1, 1)

        grid_params.addWidget(lbl_max_rpm, 0, 2)
        grid_params.addWidget(self.txt_max_rpm, 1, 2)

        grid_params.addWidget(lbl_min_duty, 2, 1)
        grid_params.addWidget(self.txt_min_duty, 3, 1)

        grid_params.addWidget(lbl_max_duty, 2, 2)
        grid_params.addWidget(self.txt_max_duty, 3, 2)

        top_layout.addLayout(grid_params)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # 2. Pjesa e Poshtme: Tabela Spindle & coolant relays
        lbl_table_title = QLabel("Spindle & coolant relays")
        lbl_table_title.setStyleSheet("font-weight: bold; color: #CCCCCC;")
        main_layout.addWidget(lbl_table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Signal",
            "Enable",
            "Pin",
            "Active Low",
            "ON delay",
            "OFF delay",
        ])

        self.table.setRowCount(len(self.relay_signals))
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

        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 75)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 90)

        main_layout.addWidget(self.table)

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
        # Leximi i kontrollit të motorit
        mode = "NONE"
        if self.config_manager:
            mode = self.config_manager.get("SPINDLE", "ControlMode", fallback="NONE").upper()

        if mode == "STEP_DIR":
            self.rb_step_dir.setChecked(True)
        elif mode == "PWM":
            self.rb_pwm.setChecked(True)
        else:
            self.rb_none.setChecked(True)

        if self.config_manager:
            self.txt_pwm_freq.setText(self.config_manager.get("SPINDLE", "PWMFrequency", fallback="10000"))
            self.txt_min_rpm.setText(self.config_manager.get("SPINDLE", "MinRPM", fallback="0"))
            self.txt_max_rpm.setText(self.config_manager.get("SPINDLE", "MaxRPM", fallback="8000"))
            self.txt_min_duty.setText(self.config_manager.get("SPINDLE", "MinDuty", fallback="0"))
            self.txt_max_duty.setText(self.config_manager.get("SPINDLE", "MaxDuty", fallback="100"))

        # Leximi i relave për tabelën
        defaults = {
            "M3 (CW)": (True, 0, False, 1000, 1000),
            "M4 (CCW)": (True, 0, False, 1000, 1000),
            "M7 (Mist)": (False, 0, False, 0, 0),
            "M8 (Flood)": (False, 0, False, 0, 0),
        }

        for row, sig_name in enumerate(self.relay_signals):
            def_en, def_pin, def_al, def_on, def_off = defaults[sig_name]

            section = f"RELAY_{sig_name.split()[0]}"
            is_enabled = def_en
            pin = def_pin
            active_low = def_al
            on_delay = def_on
            off_delay = def_off

            if self.config_manager:
                is_enabled = self.config_manager.get_boolean(section, "Enable", def_en)
                pin = int(self.config_manager.get(section, "Pin", str(def_pin)))
                active_low = self.config_manager.get_boolean(section, "ActiveLow", def_al)
                on_delay = int(self.config_manager.get(section, "ONDelay", str(def_on)))
                off_delay = int(self.config_manager.get(section, "OFFDelay", str(def_off)))

            # 0. Signal Name
            item_name = QTableWidgetItem(sig_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            # 1. Enable QCheckBox
            self._add_checkbox_centered(row, 1, is_enabled)

            # 2. Pin SpinBox
            spin_pin = QSpinBox()
            spin_pin.setRange(0, 255)
            spin_pin.setValue(pin)
            spin_pin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 2, spin_pin)

            # 3. Active Low QCheckBox
            self._add_checkbox_centered(row, 3, active_low)

            # 4. ON delay SpinBox
            spin_on = QSpinBox()
            spin_on.setRange(0, 60000)
            spin_on.setValue(on_delay)
            spin_on.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 4, spin_on)

            # 5. OFF delay SpinBox
            spin_off = QSpinBox()
            spin_off.setRange(0, 60000)
            spin_off.setValue(off_delay)
            spin_off.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 5, spin_off)

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

        mode = "NONE"
        if self.rb_step_dir.isChecked():
            mode = "STEP_DIR"
        elif self.rb_pwm.isChecked():
            mode = "PWM"

        self.config_manager.set("SPINDLE", "ControlMode", mode)
        self.config_manager.set("SPINDLE", "PWMFrequency", self.txt_pwm_freq.text())
        self.config_manager.set("SPINDLE", "MinRPM", self.txt_min_rpm.text())
        self.config_manager.set("SPINDLE", "MaxRPM", self.txt_max_rpm.text())
        self.config_manager.set("SPINDLE", "MinDuty", self.txt_min_duty.text())
        self.config_manager.set("SPINDLE", "MaxDuty", self.txt_max_duty.text())

        for row, sig_name in enumerate(self.relay_signals):
            section = f"RELAY_{sig_name.split()[0]}"

            enabled = self._get_checkbox_state(row, 1)
            active_low = self._get_checkbox_state(row, 3)

            spin_pin = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
            spin_on = cast(Optional[QSpinBox], self.table.cellWidget(row, 4))
            spin_off = cast(Optional[QSpinBox], self.table.cellWidget(row, 5))

            pin = spin_pin.value() if spin_pin is not None else 0
            on_delay = spin_on.value() if spin_on is not None else 0
            off_delay = spin_off.value() if spin_off is not None else 0

            self.config_manager.set(section, "Enable", str(enabled))
            self.config_manager.set(section, "Pin", str(pin))
            self.config_manager.set(section, "ActiveLow", str(active_low))
            self.config_manager.set(section, "ONDelay", str(on_delay))
            self.config_manager.set(section, "OFFDelay", str(off_delay))