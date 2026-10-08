import os
import configparser


class ConfigManager:

  def __init__(self, profile_name="MILL"):
    self.profile_name = profile_name
    self.config_dir = "config"
    self.config_path = os.path.join(self.config_dir, f"{profile_name}.ini")
    self.config = configparser.ConfigParser()
    self.config.optionxform = lambda optionstr: optionstr

    if not os.path.exists(self.config_dir):
      os.makedirs(self.config_dir)

    self.load_config()

  def load_config(self):
    """Lexon skedarin .ini ose krijon atë me vlera standarde nëse nuk ekziston."""
    if os.path.exists(self.config_path):
      self.config.read(self.config_path)
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
        status[axis] = self.config.getboolean("AXIS_ENABLE", axis, fallback=True)
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
    return self.get("GENERAL", "MotionController", fallback="Ether-MCI")

  def set_motion_controller_type(self, controller_type: str):
    self.set("GENERAL", "MotionController", controller_type)

  def get_motion_controller_ip(self) -> str:
    return self.get("GENERAL", "ControllerIP", fallback="192.168.1.222")

  def set_motion_controller_ip(self, ip_address: str):
    self.set("GENERAL", "ControllerIP", ip_address)