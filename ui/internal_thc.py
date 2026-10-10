from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class InternalThcWidget(QWidget):
    """Faqja Internal THC për konfigurimin e sensorit analog dhe parametrave të tensionit të plazmës."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # 1. Input calibration Group
        group_calib = QGroupBox("Input calibration")
        h_calib = QHBoxLayout(group_calib)
        h_calib.setSpacing(10)

        v_analog = QVBoxLayout()
        v_analog.addWidget(QLabel("Analog input"))
        self.combo_analog = QComboBox()
        self.combo_analog.addItems(["Analog1", "Analog2"])
        self.combo_analog.setFixedWidth(100)
        v_analog.addWidget(self.combo_analog)

        v_adc = QVBoxLayout()
        v_adc.addWidget(QLabel("ADC voltage [V]"))
        self.txt_adc = QLineEdit("5")
        self.txt_adc.setFixedWidth(70)
        v_adc.addWidget(self.txt_adc)

        lbl_arrow = QLabel("=>")
        lbl_arrow.setStyleSheet("font-weight: bold; font-size: 14px;")

        v_torch = QVBoxLayout()
        v_torch.addWidget(QLabel("Torch voltage [V]"))
        self.txt_torch_v = QLineEdit("250")
        self.txt_torch_v.setFixedWidth(80)
        v_torch.addWidget(self.txt_torch_v)

        self.chk_log_v = QCheckBox("Log voltage")

        h_calib.addLayout(v_analog)
        h_calib.addLayout(v_adc)
        h_calib.addWidget(lbl_arrow, alignment=Qt.AlignmentFlag.AlignBottom)
        h_calib.addLayout(v_torch)
        h_calib.addSpacing(20)
        h_calib.addWidget(self.chk_log_v, alignment=Qt.AlignmentFlag.AlignBottom)
        h_calib.addStretch()

        main_layout.addWidget(group_calib)

        # 2. Pjesa e mesme: Nominal voltage, Hysteresis, Arc detection, Low pass filter
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(15)

        v_left_params = QVBoxLayout()
        v_left_params.setSpacing(10)

        # Nominal & Hysteresis
        h_nom = QHBoxLayout()
        lbl_nom = QLabel("Nominal torch voltage [V]:")
        self.txt_nom_v = QLineEdit("100")
        self.txt_nom_v.setFixedWidth(70)
        h_nom.addWidget(lbl_nom)
        h_nom.addWidget(self.txt_nom_v)
        h_nom.addStretch()

        h_hys = QHBoxLayout()
        lbl_hys = QLabel("Hysteresis voltage [Vpp]:")
        self.txt_hys = QLineEdit("3")
        self.txt_hys.setFixedWidth(70)
        h_hys.addWidget(lbl_hys)
        h_hys.addWidget(self.txt_hys)
        h_hys.addStretch()

        v_left_params.addLayout(h_nom)
        v_left_params.addLayout(h_hys)

        # Low pass filter
        h_lpf = QHBoxLayout()
        self.chk_lpf = QCheckBox("Low pass filter [Hz]")
        self.txt_lpf = QLineEdit("200")
        self.txt_lpf.setFixedWidth(70)
        h_lpf.addWidget(self.chk_lpf)
        h_lpf.addWidget(self.txt_lpf)
        h_lpf.addStretch()
        v_left_params.addLayout(h_lpf)

        # Kerf detect (tip saver)
        group_kerf = QGroupBox("Kerf detect (tip saver)")
        v_kerf = QVBoxLayout(group_kerf)
        v_kerf.setSpacing(8)

        self.chk_kerf = QCheckBox("Kerf detect (tip saver)")
        
        h_rise = QHBoxLayout()
        h_rise.addWidget(QLabel("Voltage rise above Vnom [%]"))
        self.txt_kerf_rise = QLineEdit("20")
        self.txt_kerf_rise.setFixedWidth(60)
        h_rise.addWidget(self.txt_kerf_rise)
        h_rise.addStretch()

        h_period = QHBoxLayout()
        h_period.addWidget(QLabel("Time period [ms]"))
        self.txt_kerf_time = QLineEdit("100")
        self.txt_kerf_time.setFixedWidth(60)
        h_period.addWidget(self.txt_kerf_time)
        h_period.addStretch()

        v_kerf.addWidget(self.chk_kerf)
        v_kerf.addLayout(h_rise)
        v_kerf.addLayout(h_period)

        v_left_params.addWidget(group_kerf)
        mid_layout.addLayout(v_left_params)

        # Pjesa e djathtë: Arc detection & Voltage range lock
        v_right_params = QVBoxLayout()
        v_right_params.setSpacing(15)

        group_arc = QGroupBox()
        v_arc = QVBoxLayout(group_arc)
        self.chk_arc_det = QCheckBox("Arc detection [+-V]\nrelative to Vnom")
        h_arc_val = QHBoxLayout()
        self.txt_arc_val = QLineEdit("50")
        self.txt_arc_val.setFixedWidth(60)
        h_arc_val.addWidget(self.txt_arc_val)
        h_arc_val.addStretch()

        h_arc_time = QHBoxLayout()
        h_arc_time.addWidget(QLabel("Detection time [ms]:"))
        self.txt_arc_time = QLineEdit("1000")
        self.txt_arc_time.setFixedWidth(60)
        h_arc_time.addWidget(self.txt_arc_time)
        h_arc_time.addStretch()

        v_arc.addWidget(self.chk_arc_det)
        v_arc.addLayout(h_arc_val)
        v_arc.addLayout(h_arc_time)
        v_right_params.addWidget(group_arc)

        group_range = QGroupBox()
        v_range = QVBoxLayout(group_range)
        self.chk_range_lock = QCheckBox("Lock THC when voltage is out of valid range")
        
        h_vmax = QHBoxLayout()
        h_vmax.addWidget(QLabel("Vmax [%Vnom]"))
        self.txt_vmax = QLineEdit("150")
        self.txt_vmax.setFixedWidth(60)
        h_vmax.addWidget(self.txt_vmax)
        h_vmax.addStretch()

        h_vmin = QHBoxLayout()
        h_vmin.addWidget(QLabel("Vmin [%Vnom]"))
        self.txt_vmin = QLineEdit("50")
        self.txt_vmin.setFixedWidth(60)
        h_vmin.addWidget(self.txt_vmin)
        h_vmin.addStretch()

        v_range.addWidget(self.chk_range_lock)
        v_range.addLayout(h_vmax)
        v_range.addLayout(h_vmin)
        v_right_params.addWidget(group_range)

        mid_layout.addLayout(v_right_params)
        main_layout.addLayout(mid_layout)
        main_layout.addStretch()

    def load_data(self):
        if not self.config_manager:
            return

        self.txt_adc.setText(self.config_manager.get("INTERNAL_THC", "ADCVoltage", fallback="5"))
        self.txt_torch_v.setText(self.config_manager.get("INTERNAL_THC", "TorchVoltage", fallback="250"))
        self.chk_log_v.setChecked(self.config_manager.get_boolean("INTERNAL_THC", "LogVoltage", False))

        self.txt_nom_v.setText(self.config_manager.get("INTERNAL_THC", "NominalVoltage", fallback="100"))
        self.txt_hys.setText(self.config_manager.get("INTERNAL_THC", "HysteresisVoltage", fallback="3"))

        self.chk_lpf.setChecked(self.config_manager.get_boolean("INTERNAL_THC", "LowPassFilterEnable", False))
        self.txt_lpf.setText(self.config_manager.get("INTERNAL_THC", "LowPassFilterHz", fallback="200"))

        self.chk_kerf.setChecked(self.config_manager.get_boolean("INTERNAL_THC", "KerfDetectEnable", False))
        self.txt_kerf_rise.setText(self.config_manager.get("INTERNAL_THC", "KerfVoltageRisePct", fallback="20"))
        self.txt_kerf_time.setText(self.config_manager.get("INTERNAL_THC", "KerfTimePeriodMS", fallback="100"))

        self.chk_arc_det.setChecked(self.config_manager.get_boolean("INTERNAL_THC", "ArcDetectEnable", False))
        self.txt_arc_val.setText(self.config_manager.get("INTERNAL_THC", "ArcDetectVolts", fallback="50"))
        self.txt_arc_time.setText(self.config_manager.get("INTERNAL_THC", "ArcDetectTimeMS", fallback="1000"))

        self.chk_range_lock.setChecked(self.config_manager.get_boolean("INTERNAL_THC", "RangeLockEnable", False))
        self.txt_vmax.setText(self.config_manager.get("INTERNAL_THC", "VMaxPct", fallback="150"))
        self.txt_vmin.setText(self.config_manager.get("INTERNAL_THC", "VMinPct", fallback="50"))

    def save_settings(self):
        if not self.config_manager:
            return

        self.config_manager.set("INTERNAL_THC", "ADCVoltage", self.txt_adc.text())
        self.config_manager.set("INTERNAL_THC", "TorchVoltage", self.txt_torch_v.text())
        self.config_manager.set("INTERNAL_THC", "LogVoltage", str(self.chk_log_v.isChecked()))

        self.config_manager.set("INTERNAL_THC", "NominalVoltage", self.txt_nom_v.text())
        self.config_manager.set("INTERNAL_THC", "HysteresisVoltage", self.txt_hys.text())

        self.config_manager.set("INTERNAL_THC", "LowPassFilterEnable", str(self.chk_lpf.isChecked()))
        self.config_manager.set("INTERNAL_THC", "LowPassFilterHz", self.txt_lpf.text())

        self.config_manager.set("INTERNAL_THC", "KerfDetectEnable", str(self.chk_kerf.isChecked()))
        self.config_manager.set("INTERNAL_THC", "KerfVoltageRisePct", self.txt_kerf_rise.text())
        self.config_manager.set("INTERNAL_THC", "KerfTimePeriodMS", self.txt_kerf_time.text())

        self.config_manager.set("INTERNAL_THC", "ArcDetectEnable", str(self.chk_arc_det.isChecked()))
        self.config_manager.set("INTERNAL_THC", "ArcDetectVolts", self.txt_arc_val.text())
        self.config_manager.set("INTERNAL_THC", "ArcDetectTimeMS", self.txt_arc_time.text())

        self.config_manager.set("INTERNAL_THC", "RangeLockEnable", str(self.chk_range_lock.isChecked()))
        self.config_manager.set("INTERNAL_THC", "VMaxPct", self.txt_vmax.text())
        self.config_manager.set("INTERNAL_THC", "VMinPct", self.txt_vmin.text())