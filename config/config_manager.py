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
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigManager:

    def __init__(self, profile_name="MILL"):
        self.profile_name = profile_name

        # Struktura fiks si te mikrocNC: dosja macros/<ProfileName>/
        self.base_dir = get_base_dir()
        self.macros_dir = os.path.join(self.base_dir, "macros")
        self.profile_dir = os.path.join(self.macros_dir, self.profile_name)
        self.config_dir = os.path.join(self.base_dir, "config")
        # Skedari kryesor .ini ruhet në rrënjë ose te config (këtu e ruajmë te base_dir ose config)
        self.config_path = os.path.join(self.config_dir, f"{profile_name}.ini")

        # Skedarët e veçantë brenda dosjes së profilit në macros/
        self.tooltable_path = os.path.join(self.profile_dir, "tooltable.cfg")
        self.fixtures_path = os.path.join(self.profile_dir, "fixtures.cfg")
        self.persistent_path = os.path.join(self.profile_dir, "persistent.cfg")

        # Sigurohemi që të ekzistojnë dosjet
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir, exist_ok=True)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda optionstr: optionstr

        self.load_config()
        self._init_default_cfgs()

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

    def _init_default_cfgs(self):
        """Krijon skedarët bazë .cfg (tooltable, fixtures, persistent) nëse mungojnë."""
        if not os.path.exists(self.tooltable_path):
            cfg_tool = configparser.ConfigParser()
            cfg_tool.optionxform = lambda optionstr: optionstr
            for i in range(8):
                section = f"Tool{i}"
                cfg_tool[section] = {
                    "Info": "Reference tool" if i == 0 else "Info",
                    "Xoff": "0.000000",
                    "Yoff": "0.000000",
                    "Zoff": "0.000000",
                    "Diameter": "0.000000"
                }
            with open(self.tooltable_path, "w", encoding="utf-8") as f:
                cfg_tool.write(f)

        if not os.path.exists(self.fixtures_path):
            cfg_fix = configparser.ConfigParser()
            cfg_fix.optionxform = lambda optionstr: optionstr
            for i in range(1, 8):
                section = f"Fixture{i}"
                cfg_fix[section] = {
                    "X": "250.000000" if i == 1 else "0.000000",
                    "Y": "100.000000" if i == 1 else "0.000000",
                    "Z": "50.000000" if i == 1 else "0.000000",
                    "A": "0.000000",
                    "B": "0.000000",
                    "C": "0.000000"
                }
            with open(self.fixtures_path, "w", encoding="utf-8") as f:
                cfg_fix.write(f)

        if not os.path.exists(self.persistent_path):
            cfg_per = configparser.ConfigParser()
            cfg_per.optionxform = lambda optionstr: optionstr
            cfg_per["Persistent"] = {"LastGCode": "", "LastLoadedDir": ""}
            with open(self.persistent_path, "w", encoding="utf-8") as f:
                cfg_per.write(f)

    # -------------------------------------------------------------------------
    # METODAT PËR TOOL TABLE (Lexim/Shkrim vetëm te tooltable.cfg)
    # -------------------------------------------------------------------------
    def get_tool_param(self, tool_no: int, param: str, fallback: str = "0.000000") -> str:
        """Lexon një parametër të mjetit nga tooltable.cfg."""
        cfg_tool = configparser.ConfigParser()
        cfg_tool.optionxform = lambda optionstr: optionstr
        if os.path.exists(self.tooltable_path):
            cfg_tool.read(self.tooltable_path, encoding="utf-8")
        
        section = f"Tool{tool_no}"
        return cfg_tool.get(section, param, fallback=fallback)

    def set_tool_param(self, tool_no: int, param: str, value: str):
        """Ruan parametrin e mjetit direkt te tooltable.cfg (pa prekur .ini)."""
        cfg_tool = configparser.ConfigParser()
        cfg_tool.optionxform = lambda optionstr: optionstr
        if os.path.exists(self.tooltable_path):
            cfg_tool.read(self.tooltable_path, encoding="utf-8")

        section = f"Tool{tool_no}"
        if not cfg_tool.has_section(section):
            cfg_tool.add_section(section)
        
        cfg_tool.set(section, param, str(value))
        with open(self.tooltable_path, "w", encoding="utf-8") as f:
            cfg_tool.write(f)

    # -------------------------------------------------------------------------
    # METODAT PËR FIXTURES (Lexim/Shkrim vetëm te fixtures.cfg)
    # -------------------------------------------------------------------------
    def get_fixture_param(self, fixture_no: int, param: str, fallback: str = "0.000000") -> str:
        """Lexon një parametër të fiksuesit nga fixtures.cfg."""
        cfg_fix = configparser.ConfigParser()
        cfg_fix.optionxform = lambda optionstr: optionstr
        if os.path.exists(self.fixtures_path):
            cfg_fix.read(self.fixtures_path, encoding="utf-8")

        section = f"Fixture{fixture_no}"
        return cfg_fix.get(section, param, fallback=fallback)

    def set_fixture_param(self, fixture_no: int, param: str, value: str):
        """Ruan parametrin e fiksuesit direkt te fixtures.cfg (pa prekur .ini)."""
        cfg_fix = configparser.ConfigParser()
        cfg_fix.optionxform = lambda optionstr: optionstr
        if os.path.exists(self.fixtures_path):
            cfg_fix.read(self.fixtures_path, encoding="utf-8")

        section = f"Fixture{fixture_no}"
        if not cfg_fix.has_section(section):
            cfg_fix.add_section(section)

        cfg_fix.set(section, param, str(value))
        with open(self.fixtures_path, "w", encoding="ubf-8") if False else open(self.fixtures_path, "w", encoding="utf-8") as f:
            cfg_fix.write(f)

    def create_default_profile(self):
        """Krijon një profil standard nëse skedari .ini mungon."""
        self.config["GENERAL"] = {
            "MotionController": "Ether-MCI",
            "ControllerIP": "192.168.1.222",
            "BusinessName": "",
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
        """Kthen një dictionary me statusin True/False për secilin aks."""
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
        """Lexon 'Type' nga seksioni [MotionController]."""
        if self.config.has_option("MotionController", "Type"):
            return self.config.get("MotionController", "Type")
        elif self.config.has_option("GENERAL", "MotionController"):
            return self.config.get("GENERAL", "MotionController")
        return "2"  # Default ETH-MCI

    def get_motion_controller_ip(self) -> str:
        """Lexon 'IP' nga seksioni [MotionController]."""
        ip_hex = None
        if self.config.has_option("MotionController", "IP"):
            ip_hex = self.config.get("MotionController", "IP")
        elif self.config.has_option("GENERAL", "ControllerIP"):
            ip_hex = self.config.get("GENERAL", "ControllerIP")

        if ip_hex:
            return hex_to_ip(ip_hex)
        return "192.168.1.222"

    def set_motion_controller_type(self, controller_type: str):
        """Ruan 'Type' te seksioni [MotionController]."""
        if not self.config.has_section("MotionController"):
            self.config.add_section("MotionController")

        self.config.set("MotionController", "Type", str(controller_type))

        if self.config.has_option("GENERAL", "MotionController"):
            self.config.remove_option("GENERAL", "MotionController")

        self.save_config()

    def set_motion_controller_ip(self, ip_hex: str):
        """Ruan 'IP' te seksioni [MotionController]."""
        if not self.config.has_section("MotionController"):
            self.config.add_section("MotionController")

        self.config.set("MotionController", "IP", str(ip_hex))

        if self.config.has_option("GENERAL", "ControllerIP"):
            self.config.remove_option("GENERAL", "ControllerIP")

        self.save_config()

    def get_max_freq(self) -> int:
        """Lexon 'MaxFreq' nga seksioni [MotionController]."""
        if self.config.has_option("MotionController", "MaxFreq"):
            try:
                return self.config.getint("MotionController", "MaxFreq")
            except ValueError:
                return 0
        return 0

    def set_max_freq(self, val: int):
        """Ruan 'MaxFreq' te seksioni [MotionController]."""
        if not self.config.has_section("MotionController"):
            self.config.add_section("MotionController")

        self.config.set("MotionController", "MaxFreq", str(val))
        self.save_config()

    def get_business_name(self) -> str:
        """Lexon emrin e biznesit nga skedari .ini."""
        return self.config.get("GENERAL", "BusinessName", fallback="")

    def set_business_name(self, name: str):
        """Ruan emrin e biznesit në skedarin .ini."""
        if not self.config.has_section("GENERAL"):
            self.config.add_section("GENERAL")
        self.config.set("GENERAL", "BusinessName", name.strip())
        self.save_config()