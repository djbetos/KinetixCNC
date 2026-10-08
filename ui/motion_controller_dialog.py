from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, 
                             QLabel, QLineEdit, QPushButton, QButtonGroup, QGroupBox)
from PySide6.QtCore import Qt

class MotionControllerDialog(QDialog):
    def __init__(self, current_controller="ETH-MCI", current_ip="192.168.1.222", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select motion controller")
        self.setFixedSize(320, 260)

        self.selected_controller = current_controller
        self.ip_address = current_ip

        # Stili vizual identik me pamjen
        self.setStyleSheet("""
            QDialog { background-color: #F0F0F0; color: #000000; font-family: 'Segoe UI', sans-serif; }
            QRadioButton { color: #000000; font-size: 13px; font-weight: normal; margin-bottom: 5px; }
            QLabel { color: #000000; font-size: 12px; }
            QLineEdit { background-color: #FFFFFF; color: #000000; border: 1px solid #7A7A7A; border-radius: 2px; padding: 3px; font-size: 13px; font-weight: bold; }
            QPushButton { background-color: #E1E1E1; color: #000000; border: 1px solid #ADADAD; border-radius: 3px; min-width: 75px; padding: 5px; font-size: 12px; }
            QPushButton:hover { background-color: #E5F1FB; border-color: #0078D7; }
            QPushButton:pressed { background-color: #CCE4F7; border-color: #005499; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(10)

        # Radio Buttons Group
        self.btn_group = QButtonGroup(self)

        self.rb_demo = QRadioButton("DEMO (controller simulation)")
        self.rb_usbmc = QRadioButton("USB-MC based controller")
        self.rb_ethmci = QRadioButton("ETH-MCI")
        self.rb_ethbox = QRadioButton("ETH-MC(BOX)")

        self.btn_group.addButton(self.rb_demo, 1)
        self.btn_group.addButton(self.rb_usbmc, 2)
        self.btn_group.addButton(self.rb_ethmci, 3)
        self.btn_group.addButton(self.rb_ethbox, 4)

        # Zgjedhja e paracaktuar
        if current_controller == "DEMO (controller simulation)":
            self.rb_demo.setChecked(True)
        elif current_controller == "USB-MC based controller":
            self.rb_usbmc.setChecked(True)
        elif current_controller == "ETH-MC(BOX)":
            self.rb_ethbox.setChecked(True)
        else:
            self.rb_ethmci.setChecked(True)

        layout.addWidget(self.rb_demo)
        layout.addWidget(self.rb_usbmc)
        layout.addWidget(self.rb_ethmci)
        layout.addWidget(self.rb_ethbox)

        layout.addSpacing(10)

        # IP Address Section
        lbl_ip = QLabel("IP address for Ethernet controller:")
        lbl_ip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_ip)

        self.txt_ip = QLineEdit()
        self.txt_ip.setText(self.ip_address)
        self.txt_ip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_ip.setFixedWidth(200)
        
        ip_container = QHBoxLayout()
        ip_container.addStretch()
        ip_container.addWidget(self.txt_ip)
        ip_container.addStretch()
        layout.addLayout(ip_container)

        layout.addSpacing(10)

        # OK and Cancel Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Aktivizimi/Çaktivizimi i fushës IP bazuar në kontrolluesin e zgjedhur
        self.btn_group.idToggled.connect(self.update_ip_field_state)
        self.update_ip_field_state()

    def update_ip_field_state(self):
        # Mundëso IP vetëm nëse është zgjedhur Ether-MCI ose ETH-MC(BOX)
        is_ethernet = self.rb_ethmci.isChecked() or self.rb_ethbox.isChecked()
        self.txt_ip.setEnabled(is_ethernet)

    def get_selected_data(self):
        selected_button = self.btn_group.checkedButton()
        controller_name = selected_button.text() if selected_button else "ETH-MCI"
        return controller_name, self.txt_ip.text().strip()