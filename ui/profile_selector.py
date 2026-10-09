import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ProfileSelectorDialog(QDialog):

  def __init__(self):
    super().__init__()
    self.selected_profile = None
    self.setWindowTitle("CNC Profile Manager")
    self.resize(380, 420)

    # Stili Dark Industrial
    self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QLabel { font-size: 13px; font-weight: bold; color: #CCCCCC; }
            QListWidget { background-color: #252526; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 4px; font-size: 13px; }
            QListWidget::item:selected { background-color: #007ACC; color: white; }
            QPushButton { background-color: #333337; color: white; border: 1px solid #555555; padding: 7px 12px; border-radius: 3px; font-weight: bold; }
            QPushButton:hover { background-color: #007ACC; border-color: #007ACC; }
        """)

    layout = QVBoxLayout()
    layout.addWidget(QLabel("Zgjidhni ose Krijoni një Profil CNC:"))

    self.profile_list = QListWidget()
    layout.addWidget(self.profile_list)

    # Butonat
    btn_layout = QHBoxLayout()

    btn_new = QPushButton("New")
    btn_new.clicked.connect(self.create_new_profile)
    btn_layout.addWidget(btn_new)

    btn_load = QPushButton("Load Profile")
    btn_load.clicked.connect(self.load_selected_profile)
    btn_layout.addWidget(btn_load)

    btn_exit = QPushButton("Exit")
    btn_exit.clicked.connect(self.reject)
    btn_layout.addWidget(btn_exit)

    layout.addLayout(btn_layout)
    self.setLayout(layout)

    self.refresh_profiles()

  def get_config_dir(self):
    """Kthen rrugën absolute të folderit config ngjitur me .exe ose main.py."""
    if getattr(sys, "frozen", False):
      # Nëse po ekzekutohet si skedar i paketuar .exe
      base_dir = os.path.dirname(sys.executable)
    else:
      # Nëse po ekzekutohet si skript normal python
      base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_dir, "config")
    if not os.path.exists(config_dir):
      os.makedirs(config_dir)
    return config_dir

  def refresh_profiles(self):
    self.profile_list.clear()
    config_dir = self.get_config_dir()

    # Lexojmë profilët nga skedarët .ini
    if os.path.exists(config_dir):
      for file in os.listdir(config_dir):
        if file.endswith(".ini"):
          profile_name = os.path.splitext(file)[0]
          self.profile_list.addItem(profile_name)

    if self.profile_list.count() > 0:
      self.profile_list.setCurrentRow(0)

  def create_new_profile(self):
    name, ok = QInputDialog.getText(
        self,
        "Profil i Ri",
        "Shkruani emrin e profilit të ri (p.sh. MILL):",
    )
    if ok and name.strip():
      clean_name = name.strip().upper()
      config_dir = self.get_config_dir()
      file_path = os.path.join(config_dir, f"{clean_name}.ini")

      if os.path.exists(file_path):
        QMessageBox.warning(self, "Kujdes", "Ky profil ekziston tashmë!")
      else:
        from config.config_manager import ConfigManager

        cfg = ConfigManager(clean_name)
        cfg.create_default_profile()  # Krijon dhe ruan fizikisht skedarin .ini
        self.refresh_profiles()

  def load_selected_profile(self):
    current_item = self.profile_list.currentItem()
    if current_item:
      self.selected_profile = current_item.text()
      self.accept()
    else:
      QMessageBox.warning(
          self, "Kujdes", "Ju lutem zgjidhni një profil nga lista!"
      )