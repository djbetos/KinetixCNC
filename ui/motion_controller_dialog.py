import socket
import struct
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


# =========================================================================
# FUNKSIONET NDIHMËSE PËR KONVERTIMIN E IP DHE TYPE
# =========================================================================
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


# Mapimi i tipeve sipas mikroCNC / AudioMS
CONTROLLER_TYPE_MAP = {
    0: "DEMO",
    1: "USB-MC",
    2: "ETH-MCI",
    3: "ETH-MC(BOX)",
}


class MotionControllerDialog(QDialog):

  def __init__(
      self,
      current_controller="ETH-MCI",
      current_ip="192.168.1.222",
      parent=None,
  ):
    super().__init__(parent)
    self.setWindowTitle("Select motion controller")
    self.setFixedSize(320, 260)

    # Konvertojmë IP-në nëse vjen si HEX nga skedari .ini
    self.ip_address = hex_to_ip(str(current_ip))

    # Konvertojmë Controller Type nëse vjen si numër (string ose int) nga .ini
    if str(current_controller).isdigit():
      self.selected_controller = CONTROLLER_TYPE_MAP.get(
          int(current_controller), "ETH-MCI"
      )
    else:
      self.selected_controller = current_controller

    # Stili vizual
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

    # Identyfikuesit numerikë për secilin buton
    self.btn_group.addButton(self.rb_demo, 0)
    self.btn_group.addButton(self.rb_usbmc, 1)
    self.btn_group.addButton(self.rb_ethmci, 2)
    self.btn_group.addButton(self.rb_ethbox, 3)

    # Zgjedhja e paracaktuar bazohet në vlerën e konvertuar
    ctrl_upper = str(self.selected_controller).upper()
    if "DEMO" in ctrl_upper:
      self.rb_demo.setChecked(True)
    elif "USB" in ctrl_upper:
      self.rb_usbmc.setChecked(True)
    elif "BOX" in ctrl_upper:
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

    self.btn_group.idToggled.connect(self.update_ip_field_state)
    self.update_ip_field_state()

  def update_ip_field_state(self):
    is_ethernet = self.rb_ethmci.isChecked() or self.rb_ethbox.isChecked()
    self.txt_ip.setEnabled(is_ethernet)

  def get_selected_data(self):
    """Kthen të dhënat e konvertuara saktësisht siç i kërkon MikroCNC / AudioMS."""
    ctrl_id = self.btn_group.checkedId()
    if ctrl_id == -1:
      ctrl_id = 2  # Default ETH-MCI

    ip_str = self.txt_ip.text().strip()
    ip_hex = ip_to_hex(ip_str)

    # Kthen (Type_ID, IP_HEX, Human_Name, Standard_IP)
    # kjo i jep mundësi çdo mekamizmi ruajtës ta përdorë sipas nevojës
    return {
        "type_id": str(ctrl_id),
        "ip_hex": ip_hex,
        "controller_name": CONTROLLER_TYPE_MAP.get(ctrl_id, "ETH-MCI"),
        "ip_str": ip_str,
    }


# =========================================================================
# SI DUHET TË RUAJË MAIN WINDOW OSE CONFIG MANAGER KËTË DIALOG:
# =========================================================================
# dialog = MotionControllerDialog(current_controller, current_ip, self)
# if dialog.exec():
#     data = dialog.get_selected_data()
#
#     # Ruajtja e saktë te skedari .ini sipas AudioMS / MikroCNC:
#     config_manager.set("MotionController", "Type", data["type_id"])   # p.sh. "2"
#     config_manager.set("MotionController", "IP", data["ip_hex"])       # p.sh. "C0A801DE"
#     config_manager.save_config()