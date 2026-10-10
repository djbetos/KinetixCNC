from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class GeneralThcWidget(QWidget):
    """Faqja General THC për konfigurimin e kontrollit të lartësisë së plazmës."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. GroupBox për llojin e rregulluesit THC
        group_type = QGroupBox("THC regulator type")
        v_type = QVBoxLayout(group_type)
        v_type.setSpacing(8)

        self.rb_external = QRadioButton("External THC (use digital inputs for Up/Down control)")
        self.rb_internal = QRadioButton("Internal THC (use THC voltage sensor via analog input)")
        self.rb_external.setChecked(True)

        v_type.addWidget(self.rb_external)
        v_type.addWidget(self.rb_internal)
        main_layout.addWidget(group_type)

        # 2. Pierce delay [ms]
        h_pierce = QHBoxLayout()
        lbl_pierce = QLabel("Pierce delay [ms]")
        lbl_pierce.setStyleSheet("color: #CCCCCC;")
        self.txt_pierce_delay = QLineEdit("1000")
        self.txt_pierce_delay.setFixedWidth(90)

        h_pierce.addWidget(lbl_pierce)
        h_pierce.addWidget(self.txt_pierce_delay)
        h_pierce.addStretch()
        main_layout.addLayout(h_pierce)

        # 3. Checkboxes për opsionet e THC
        self.chk_wait_arc = QCheckBox("Wait for ArcOK signal")
        self.chk_lock_thc = QCheckBox("Lock THC from g-code by fast port#6 commands")
        self.chk_ramped_thc = QCheckBox("Ramped THC moves")

        for chk in (self.chk_wait_arc, self.chk_lock_thc, self.chk_ramped_thc):
            chk.setStyleSheet("color: #CCCCCC; font-size: 12px;")
            main_layout.addWidget(chk)

        main_layout.addStretch()

    def load_data(self):
        if not self.config_manager:
            return

        reg_type = self.config_manager.get("THC", "RegulatorType", fallback="EXTERNAL").upper()
        if "INT" in reg_type:
            self.rb_internal.setChecked(True)
        else:
            self.rb_external.setChecked(True)

        self.txt_pierce_delay.setText(self.config_manager.get("THC", "PierceDelay", fallback="1000"))
        self.chk_wait_arc.setChecked(self.config_manager.get_boolean("THC", "WaitArcOK", True))
        self.chk_lock_thc.setChecked(self.config_manager.get_boolean("THC", "LockFromGCode", False))
        self.chk_ramped_thc.setChecked(self.config_manager.get_boolean("THC", "RampedMoves", True))

    def save_settings(self):
        if not self.config_manager:
            return

        reg_type = "INTERNAL" if self.rb_internal.isChecked() else "EXTERNAL"
        self.config_manager.set("THC", "RegulatorType", reg_type)
        self.config_manager.set("THC", "PierceDelay", self.txt_pierce_delay.text())
        self.config_manager.set("THC", "WaitArcOK", str(self.chk_wait_arc.isChecked()))
        self.config_manager.set("THC", "LockFromGCode", str(self.chk_lock_thc.isChecked()))
        self.config_manager.set("THC", "RampedMoves", str(self.chk_ramped_thc.isChecked()))