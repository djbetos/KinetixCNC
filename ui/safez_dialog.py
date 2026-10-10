from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class SafeZDialog(QDialog):
    """Dritarja SafeZ setup për konfigurimin e pozicionit të sigurt të aksit Z."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("SafeZ setup")
        self.resize(360, 320)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. Enable safe Z moves
        self.chk_enable_safe_z = QCheckBox("Enable safe Z moves")
        main_layout.addWidget(self.chk_enable_safe_z)

        # 2. GroupBox: Safe Z position is in:
        group_pos = QGroupBox("Safe Z position is in:")
        v_pos = QVBoxLayout(group_pos)
        v_pos.setSpacing(8)

        self.rb_machine = QRadioButton("Machine coordinates")
        self.rb_work = QRadioButton("Work coordinates")
        self.rb_relative = QRadioButton("Relative to current position")
        self.rb_machine.setChecked(True)

        v_pos.addWidget(self.rb_machine)
        v_pos.addWidget(self.rb_work)
        v_pos.addWidget(self.rb_relative)
        main_layout.addWidget(group_pos)

        # 3. SafeZ value [ ] mm
        h_val = QHBoxLayout()
        lbl_val = QLabel("SafeZ value")
        self.txt_safez_val = QLineEdit("0")
        self.txt_safez_val.setFixedWidth(90)
        lbl_unit = QLabel("mm")

        h_val.addWidget(lbl_val)
        h_val.addWidget(self.txt_safez_val)
        h_val.addWidget(lbl_unit)
        h_val.addStretch()
        main_layout.addLayout(h_val)

        # 4. Go to SafeZ location when STOP button is pressed
        self.chk_stop_safe_z = QCheckBox("Go to SafeZ location when STOP button is pressed")
        main_layout.addWidget(self.chk_stop_safe_z)

        main_layout.addStretch()

        # 5. Butonat OK / Cancel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setFixedWidth(80)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

    def load_data(self):
        if not self.config_manager:
            return

        enable_safe = self.config_manager.get_boolean("SAFE_Z", "Enable", False)
        self.chk_enable_safe_z.setChecked(enable_safe)

        pos_mode = self.config_manager.get("SAFE_Z", "PositionMode", "MACHINE").upper()
        if "WORK" in pos_mode:
            self.rb_work.setChecked(True)
        elif "REL" in pos_mode:
            self.rb_relative.setChecked(True)
        else:
            self.rb_machine.setChecked(True)

        val = self.config_manager.get("SAFE_Z", "Value", "0")
        self.txt_safez_val.setText(val)

        stop_safe = self.config_manager.get_boolean("SAFE_Z", "GoToOnStop", False)
        self.chk_stop_safe_z.setChecked(stop_safe)

    def accept(self):
        if self.config_manager:
            self.config_manager.set("SAFE_Z", "Enable", str(self.chk_enable_safe_z.isChecked()))
            
            mode = "MACHINE"
            if self.rb_work.isChecked():
                mode = "WORK"
            elif self.rb_relative.isChecked():
                mode = "RELATIVE"
            self.config_manager.set("SAFE_Z", "PositionMode", mode)

            self.config_manager.set("SAFE_Z", "Value", self.txt_safez_val.text())
            self.config_manager.set("SAFE_Z", "GoToOnStop", str(self.chk_stop_safe_z.isChecked()))

        super().accept()