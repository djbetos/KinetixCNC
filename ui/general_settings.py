import socket
import struct
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


def ip_to_hex(ip_str: str) -> str:
    """Konverton '192.168.1.222' -> 'C0A801DE'"""
    try:
        packed = socket.inet_aton(ip_str.strip())
        return struct.pack("!I", struct.unpack("!I", packed)[0]).hex().upper()
    except Exception:
        return "C0A801DE"


def hex_to_ip(hex_str: str) -> str:
    """Konverton 'C0A801DE' -> '192.168.1.222'"""
    try:
        clean_hex = hex_str.strip()
        if "." in clean_hex:
            return clean_hex
        packed = bytes.fromhex(clean_hex)
        return socket.inet_ntoa(packed)
    except Exception:
        return "192.168.1.222"


CONTROLLER_TYPE_MAP = {
    "DEMO": 0,
    "USB-MC": 1,
    "ETH-MCI": 2,
    "ETH-MC(BOX)": 3,
}

REVERSE_CONTROLLER_MAP = {
    0: "DEMO",
    1: "USB-MC",
    2: "ETH-MCI",
    3: "ETH-MC(BOX)",
}


class GeneralSettingsWidget(QWidget):
    """Faqja General Settings."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        lbl_gcode = QLabel("G-code init string:")
        self.txt_gcode_init = QLineEdit("G17 G64 G49 G40")

        main_layout.addWidget(lbl_gcode)
        main_layout.addWidget(self.txt_gcode_init)

        mid_layout = QHBoxLayout()

        group_tool = QGroupBox("Tool change (M6)")
        layout_tool = QVBoxLayout()

        self.rb_ignore_tc = QRadioButton("Ignore tool change")
        self.rb_ignore_tc.setChecked(True)
        self.rb_stop_tc = QRadioButton("Stop and wait for START")

        pos_layout = QHBoxLayout()
        self.txt_x = QLineEdit("0")
        self.txt_y = QLineEdit("0")
        self.txt_z = QLineEdit("0")
        for txt in (self.txt_x, self.txt_y, self.txt_z):
            txt.setFixedWidth(50)

        pos_layout.addWidget(QLabel("X"))
        pos_layout.addWidget(self.txt_x)
        pos_layout.addWidget(QLabel("Y"))
        pos_layout.addWidget(self.txt_y)
        pos_layout.addWidget(QLabel("Z"))
        pos_layout.addWidget(self.txt_z)
        pos_layout.addStretch()

        self.rb_goto_loc = QRadioButton("Goto location (machine coord.)")
        self.rb_atc = QRadioButton("Automatic Tool Changer")

        layout_tool.addWidget(self.rb_ignore_tc)
        layout_tool.addWidget(self.rb_stop_tc)
        layout_tool.addLayout(pos_layout)
        layout_tool.addWidget(self.rb_goto_loc)
        layout_tool.addWidget(self.rb_atc)
        group_tool.setLayout(layout_tool)

        group_laser = QGroupBox("Laser options")
        layout_laser = QVBoxLayout()
        self.chk_laser = QCheckBox(
            "Gray level laser engraving (A axis controls PWM duty cycle)"
        )
        layout_laser.addWidget(self.chk_laser)
        layout_laser.addStretch()
        group_laser.setLayout(layout_laser)

        mid_layout.addWidget(group_tool, stretch=1)
        mid_layout.addWidget(group_laser, stretch=1)
        main_layout.addLayout(mid_layout)

        grid_layout = QGridLayout()

        self.chk_g04 = QCheckBox("G04 dwell time in seconds")
        self.chk_ignore_gcode = QCheckBox("Ignore unsupported G codes")
        self.chk_auto_limits = QCheckBox("Auto limits override")
        self.chk_auto_limits.setChecked(True)

        lbl_buffer = QLabel("Motion buffer size:")
        self.combo_buffer = QComboBox()
        self.combo_buffer.addItems(["Normal (default)", "Small", "Large"])

        lbl_freq = QLabel("Maximum step frequency:")
        self.combo_freq = QComboBox()
        self.combo_freq.addItem("125 kHz", 0)
        self.combo_freq.addItem("250 kHz", 1)

        self.chk_probe_limit = QCheckBox("Probe as limit")
        self.chk_dme = QCheckBox("Enable DME server")

        grid_layout.addWidget(self.chk_g04, 0, 0)
        grid_layout.addWidget(lbl_buffer, 0, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.combo_buffer, 0, 2)

        grid_layout.addWidget(self.chk_ignore_gcode, 1, 0)
        grid_layout.addWidget(lbl_freq, 1, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.combo_freq, 1, 2)

        grid_layout.addWidget(self.chk_auto_limits, 2, 0)
        grid_layout.addWidget(self.chk_probe_limit, 2, 2)

        grid_layout.addWidget(self.chk_dme, 3, 2)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

    def load_settings(self):
        if not self.config_manager:
            return

        gcode_init = self.config_manager.get(
            "GENERAL", "GCodeInit", fallback="G17 G64 G49 G40"
        )
        self.txt_gcode_init.setText(gcode_init)

        raw_max_freq = self.config_manager.get(
            "MotionController", "MaxFreq", fallback="0"
        )
        try:
            val_freq = int(raw_max_freq)
        except ValueError:
            val_freq = 0

        idx = self.combo_freq.findData(val_freq)
        if idx != -1:
            self.combo_freq.setCurrentIndex(idx)
        else:
            self.combo_freq.setCurrentIndex(0)

    def save_settings(self):
        if not self.config_manager:
            return

        self.config_manager.set(
            "GENERAL", "GCodeInit", self.txt_gcode_init.text()
        )
        selected_freq = self.combo_freq.currentData()
        self.config_manager.set(
            "MotionController", "MaxFreq", str(selected_freq)
        )