from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class MotionPlannerWidget(QWidget):
    """Faqja Motion planner për planifikimin e trajektores dhe shpejtësisë."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 1. Pjesa e Sipërme: Velocity ramp type & Look ahead lines
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)

        group_ramp = QGroupBox("Velocity ramp type")
        v_ramp = QVBoxLayout(group_ramp)
        self.rb_trapezoidal = QRadioButton("Trapezoidal")
        self.rb_scurve = QRadioButton("Cosine S-curve")
        self.rb_scurve.setChecked(True)
        v_ramp.addWidget(self.rb_trapezoidal)
        v_ramp.addWidget(self.rb_scurve)

        top_layout.addWidget(group_ramp)

        # Look ahead lines layout
        v_look = QVBoxLayout()
        lbl_look = QLabel("Look ahead lines:")
        lbl_look.setStyleSheet("color: #CCCCCC;")
        self.txt_look_ahead = QLineEdit("500")
        self.txt_look_ahead.setFixedWidth(100)
        v_look.addWidget(lbl_look)
        v_look.addWidget(self.txt_look_ahead)
        v_look.addStretch()

        top_layout.addLayout(v_look)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # 2. Pjesa e Poshtme: Constant velocity options
        group_cv = QGroupBox("Constant velocity options")
        grid_cv = QVBoxLayout(group_cv)
        grid_cv.setSpacing(10)
        grid_cv.setContentsMargins(15, 15, 15, 15)

        lbl_max_err = QLabel("Maximum error on corner blending:")
        h_err = QHBoxLayout()
        self.txt_max_err = QLineEdit("1")
        self.txt_max_err.setFixedWidth(80)
        h_err.addWidget(self.txt_max_err)
        h_err.addWidget(QLabel("mm"))
        h_err.addStretch()

        lbl_disable_cv = QLabel("Disable CV on angles less then:")
        h_ang = QHBoxLayout()
        self.txt_disable_cv = QLineEdit("1")
        self.txt_disable_cv.setFixedWidth(80)
        h_ang.addWidget(self.txt_disable_cv)
        h_ang.addWidget(QLabel("degrees"))
        h_ang.addStretch()

        grid_cv.addWidget(lbl_max_err)
        grid_cv.addLayout(h_err)
        grid_cv.addSpacing(10)
        grid_cv.addWidget(lbl_disable_cv)
        grid_cv.addLayout(h_ang)

        main_layout.addWidget(group_cv)
        main_layout.addStretch()

    def load_data(self):
        if not self.config_manager:
            return

        ramp_type = self.config_manager.get("MOTION", "RampType", fallback="S-CURVE").upper()
        if "TRAP" in ramp_type:
            self.rb_trapezoidal.setChecked(True)
        else:
            self.rb_scurve.setChecked(True)

        self.txt_look_ahead.setText(self.config_manager.get("MOTION", "LookAheadLines", fallback="500"))
        self.txt_max_err.setText(self.config_manager.get("MOTION", "MaxCornerError", fallback="1"))
        self.txt_disable_cv.setText(self.config_manager.get("MOTION", "DisableCVAngle", fallback="1"))

    def save_settings(self):
        if not self.config_manager:
            return

        ramp = "TRAPEZOIDAL" if self.rb_trapezoidal.isChecked() else "S-CURVE"
        self.config_manager.set("MOTION", "RampType", ramp)
        self.config_manager.set("MOTION", "LookAheadLines", self.txt_look_ahead.text())
        self.config_manager.set("MOTION", "MaxCornerError", self.txt_max_err.text())
        self.config_manager.set("MOTION", "DisableCVAngle", self.txt_disable_cv.text())