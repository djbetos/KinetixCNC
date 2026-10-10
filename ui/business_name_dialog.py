from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class BusinessNameDialog(QDialog):
    """Dritarja për vendosjen e emrit të biznesit."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Business Name")
        self.resize(320, 160)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        lbl_title = QLabel("Shkruani emrin e biznesit (p.sh. Euro Model):")
        main_layout.addWidget(lbl_title)

        self.txt_business_name = QLineEdit()
        self.txt_business_name.setPlaceholderText("Lëreni bosh për emrin standard")
        main_layout.addWidget(self.txt_business_name)

        main_layout.addStretch()

        # Butonat OK / Cancel
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
        if self.config_manager:
            b_name = self.config_manager.get_business_name()
            self.txt_business_name.setText(b_name)

    def accept(self):
        if self.config_manager:
            self.config_manager.set_business_name(self.txt_business_name.text())
        super().accept()