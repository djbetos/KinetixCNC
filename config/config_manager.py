import configparser
import os
import socket
import sys


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


def get_base_dir() -> str:
  """Kthen rrugën absolute të direktoriumit bazë (ku ndodhet .exe ose main.py)."""
  if getattr(sys, "frozen", False):
    # Ekzekutim si skedar i paketuar .exe
    return os.path.dirname(sys.executable)
  else:
    # Ekzekutim si skript normal Python
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigManager:

  def __init__(self, profile_name="MILL"):
    self.profile_name = profile_name

    # Llogaritja dinamike e rrugës së dosjes config dhe skedarit .ini
    self.config_dir = os.path.join(get_base_dir(), "config")
    self.config_path = os.path.join(self.config_dir, f"{profile_name}.ini")

    self.config = configparser.ConfigParser()
    self.config.optionxform = lambda optionstr: optionstr

    if not os.path.exists(self.config_dir):
      os.makedirs(self.config_dir)

    self.load_config()

  def load_config(self):
    """Lexon skedarin .ini ose krijon atë me vlera standarde nëse nuk ekziston."""
    if os.path.exists(self.config_path):
      self.config.read(self.config_path, encoding="utf-8")
    else:
      self.create_default_profile()

  def reload(self):
    """Riruan dhe ringarkon të gjitha të dhënat nga skedari .ini."""
    self.config = configparser.ConfigParser()
    self.config.optionxform = lambda optionstr: optionstr
    self.load_config()

  def read_config(self):
    """Thirrje alternative për ringarkimin e konfigurimit."""
    self.reload()

  def save_config(self):
    """Ruan gjendjen aktuale të ConfigParser te skedari .ini."""
    with open(self.config_path, "w", encoding="utf-8") as f:
      self.config.write(f)

  def create_default_profile(self):
    """Krijon një profil standard nëse skedari .ini mungon."""
    self.config["GENERAL"] = {
        "MotionController": "Ether-MCI",
        "ControllerIP": "192.168.1.222",
    }

    self.config["AXIS_ENABLE"] = {
        "X": "True",
        "Y": "True",
        "Z": "True",
        "A": "True",
        "B": "True",
        "C": "True",
    }

    self.save_config()

  # -------------------------------------------------------------------------
  # METODAT KRYESORE PËR BOSHTET (AXES)
  # -------------------------------------------------------------------------
  def get_axis_enable_status(self) -> dict:
    """Kthen një dictionary me statusin True/False për secilin aks: {'X': True, 'Y': True, ...}"""
    axes = ["X", "Y", "Z", "A", "B", "C"]
    status = {}

    if "AXIS_ENABLE" in self.config:
      for axis in axes:
        status[axis] = self.config.getboolean(
            "AXIS_ENABLE", axis, fallback=True
        )
    elif "AXIS" in self.config:
      for axis in axes:
        status[axis] = self.config.getboolean(
            "AXIS", f"Enable_{axis}", fallback=True
        )
    else:
      for axis in axes:
        status[axis] = True

    return status

  def set_axis_enable_status(self, axis_data: dict):
    """Ruan statusin e akseve nga dritarja e Setup te skedari .ini."""
    if "AXIS_ENABLE" not in self.config:
      self.config["AXIS_ENABLE"] = {}

    for axis, enabled in axis_data.items():
      self.config["AXIS_ENABLE"][axis] = str(bool(enabled))

    self.save_config()

  # -------------------------------------------------------------------------
  # METODAT NDIHMËSE (GETTERS & SETTERS)
  # -------------------------------------------------------------------------
  def get(self, section: str, option: str, fallback: str = "") -> str:
    """Merr vlerën string nga skedari .ini."""
    return self.config.get(section, option, fallback=fallback)

  def get_boolean(
      self, section: str, option: str, fallback: bool = False
  ) -> bool:
    """Merr vlerën boolean (True/False) nga skedari .ini."""
    try:
      return self.config.getboolean(section, option, fallback=fallback)
    except (ValueError, configparser.Error):
      return fallback

  def set(self, section: str, option: str, value: str):
    """Vendos një vlerë dhe e ruan menjëherë te skedari .ini."""
    if not self.config.has_section(section):
      self.config.add_section(section)
    self.config.set(section, option, str(value))
    self.save_config()

  def get_motion_controller_type(self) -> str:
    """Lexon 'Type' nga seksioni [MotionController] (me fallback te vetitë e vjetra nëse nuk ekziston)"""
    if self.config.has_option("MotionController", "Type"):
      return self.config.get("MotionController", "Type")
    elif self.config.has_option("GENERAL", "MotionController"):
      return self.config.get("GENERAL", "MotionController")
    return "2"  # Default ETH-MCI

  def get_motion_controller_ip(self) -> str:
    """Lexon 'IP' nga seksioni [MotionController] dhe e kthen si IP standarde e.g. '192.168.1.222'"""
    ip_hex = None
    if self.config.has_option("MotionController", "IP"):
      ip_hex = self.config.get("MotionController", "IP")
    elif self.config.has_option("GENERAL", "ControllerIP"):
      ip_hex = self.config.get("GENERAL", "ControllerIP")

    if ip_hex:
      return hex_to_ip(ip_hex)
    return "192.168.1.222"

  def set_motion_controller_type(self, controller_type: str):
    """Ruan 'Type' te seksioni [MotionController] dhe fshin çelësin e vjetër nga [GENERAL]."""
    if not self.config.has_section("MotionController"):
      self.config.add_section("MotionController")

    # Vendosim vlerën e re te [MotionController]
    self.config.set("MotionController", "Type", str(controller_type))

    # Fshijmë çelësin e vjetër te [GENERAL] nëse ekziston
    if self.config.has_option("GENERAL", "MotionController"):
      self.config.remove_option("GENERAL", "MotionController")

    self.save_config()

  def set_motion_controller_ip(self, ip_hex: str):
    """Ruan 'IP' te seksioni [MotionController] dhe fshin çelësin e vjetër nga [GENERAL]."""
    if not self.config.has_section("MotionController"):
      self.config.add_section("MotionController")

    # Vendosim vlerën e re te [MotionController]
    self.config.set("MotionController", "IP", str(ip_hex))

    # Fshijmë çelësin e vjetër te [GENERAL] nëse ekziston
    if self.config.has_option("GENERAL", "ControllerIP"):
      self.config.remove_option("GENERAL", "ControllerIP")

    self.save_config()

  def get_max_freq(self) -> int:
    """Lexon 'MaxFreq' nga seksioni [MotionController].

    Kthen 0 për 125 kHz, 1 për 250 kHz. Default është 0 (125 kHz).
    """
    if self.config.has_option("MotionController", "MaxFreq"):
      try:
        return self.config.getint("MotionController", "MaxFreq")
      except ValueError:
        return 0
    return 0

  def set_max_freq(self, val: int):
    """Ruan 'MaxFreq' (0 ose 1) te seksioni [MotionController]."""
    if not self.config.has_section("MotionController"):
      self.config.add_section("MotionController")

    self.config.set("MotionController", "MaxFreq", str(val))
    self.save_config()