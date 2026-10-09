import os
import sys
from PySide6.QtCore import QSize, Qt, QTime, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from config.config_manager import ConfigManager
from ui.jog_mpg_dialog import JogMPGDialog
from ui.motion_controller_dialog import MotionControllerDialog
from ui.profile_selector import ProfileSelectorDialog
from ui.setup_dialog import SetupDialog


class GCodeVisualizer3D(QWidget):
  """Widget për vizualizimin 2D/3D të toolpath-it sipas pamjes së mikroCNC."""

  def __init__(self, parent=None):
    super().__init__(parent)
    self.lines = []
    self.view_mode = "XY"
    self.tool_x = 0.0
    self.tool_y = 0.0
    self.tool_z = 0.0
    self.setMinimumSize(400, 400)

  def update_tool_position(self, x: float, y: float, z: float):
    """Përditëson pozicionin e kokës së veglës në vizualizues."""
    self.tool_x = x
    self.tool_y = y
    self.tool_z = z
    self.update()

  def set_gcode(self, gcode_text):
    self.lines = []
    cx, cy, cz = 0.0, 0.0, 0.0
    for line in gcode_text.splitlines():
      line = line.strip().upper()
      if any(
          line.startswith(code) for code in ["G0", "G1", "G00", "G01", "G2", "G3"]
      ):
        parts = line.split()
        nx, ny, nz = cx, cy, cz
        for p in parts:
          if p.startswith("X"):
            try:
              nx = float(p[1:])
            except ValueError:
              pass
          elif p.startswith("Y"):
            try:
              ny = float(p[1:])
            except ValueError:
              pass
          elif p.startswith("Z"):
            try:
              nz = float(p[1:])
            except ValueError:
              pass
        self.lines.append((cx, cy, cz, nx, ny, nz))
        cx, cy, cz = nx, ny, nz
    self.update()

  def set_view_mode(self, mode):
    self.view_mode = mode
    self.update()

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Sfondi i kaltër karakteristik i mikroCNC
    painter.fillRect(self.rect(), QColor("#3B629B"))

    cx, cy = self.width() // 2, self.height() // 2

    # Vizatimi i boshteve X/Y me ngjyra
    painter.setPen(QPen(QColor("#00FF00"), 2))  # Boshti Y (Gjelbër)
    painter.drawLine(cx, cy, cx, cy - 80)
    painter.drawText(cx + 5, cy - 85, "Y")

    painter.setPen(QPen(QColor("#FF3333"), 2))  # Boshti X (Kuq)
    painter.drawLine(cx, cy, cx + 80, cy)
    painter.drawText(cx + 85, cy + 5, "X")

    if not self.lines:
      return

    min_x = min(min(l[0], l[3]) for l in self.lines)
    max_x = max(max(l[0], l[3]) for l in self.lines)
    min_y = min(min(l[1], l[4]) for l in self.lines)
    max_y = max(max(l[1], l[4]) for l in self.lines)

    dx = (max_x - min_x) if (max_x - min_x) > 0 else 1.0
    dy = (max_y - min_y) if (max_y - min_y) > 0 else 1.0

    scale = min((self.width() - 80) / dx, (self.height() - 80) / dy)

    painter.setPen(QPen(QColor("#FFFFFF"), 1))
    for x1, y1, z1, x2, y2, z2 in self.lines:
      sx1 = int(cx + (x1 - min_x - dx / 2) * scale)
      sy1 = int(cy - (y1 - min_y - dy / 2) * scale)
      sx2 = int(cx + (x2 - min_x - dx / 2) * scale)
      sy2 = int(cy - (y2 - min_y - dy / 2) * scale)
      painter.drawLine(sx1, sy1, sx2, sy2)


class MainWindow(QMainWindow):

  def __init__(self, profile_name):
    super().__init__()
    self.profile_name = profile_name
    self.cfg = ConfigManager(profile_name)
    self.selected_controller = self.cfg.get_motion_controller_type()

    # Gjendjet e sistemit
    self.is_enabled = False
    self.estop_active = True  # Default E-Stop aktiv
    self.blink_state = False

    # Timer për efektin e pulsimit të butonit Enable (Green / Red)
    self.blink_timer = QTimer(self)
    self.blink_timer.setInterval(500)  # Ndërron çdo 500ms
    self.blink_timer.timeout.connect(self._toggle_enable_button_blink)

    # Deklarimi i atributeve për të parandaluar paralajmërimet e Pylance
    self.axis_positions = {
        "X": 0.0,
        "Y": 0.0,
        "Z": 0.0,
        "A": 0.0,
        "B": 0.0,
        "C": 0.0,
    }
    self.motion_controller = None
    self.jog_dialog = None
    self.visualizer = None
    self.dro_labels = {}
    self.axis_widgets = {}

    self.setWindowTitle(
        f"Kinetix CNC - Ether-MCI | Profile: [{profile_name}]"
    )
    self.resize(1400, 850)

    # Stili Dark Industrial (QSS)
    self.setStyleSheet("""
            QMainWindow { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            
            QMenuBar { background-color: #1E1E1E; color: #CCCCCC; font-size: 13px; border-bottom: 1px solid #333333; }
            QMenuBar::item { padding: 5px 12px; background: transparent; }
            QMenuBar::item:selected { background-color: #007ACC; color: white; }
            
            QMenu { background-color: #1E1E1E; color: #CCCCCC; border: 1px solid #333333; }
            QMenu::item { padding: 6px 25px; }
            QMenu::item:selected { background-color: #007ACC; color: white; }
            QMenu::item:disabled { color: #555555; }
            QMenu::separator { height: 1px; background-color: #333333; margin: 4px 0px; }
            
            QGroupBox { border: 1px solid #333333; border-radius: 4px; margin-top: 8px; font-weight: bold; color: #007ACC; font-size: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            
            QPushButton { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 3px; font-size: 12px; font-weight: bold; padding: 5px 8px; }
            QPushButton:hover { background-color: #007ACC; border-color: #007ACC; }
            QPushButton:pressed { background-color: #005A9E; }
            
            QLineEdit, QComboBox, QPlainTextEdit { background-color: #252526; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 3px; font-family: 'Consolas', monospace; font-size: 12px; }
            QLabel { color: #CCCCCC; }
            QStatusBar { background-color: #252526; color: #CCCCCC; font-size: 11px; }
        """)

    # 1. Menya Kryesore
    self.create_menu_bar()

    # 2. Ndërtimi i Ndërfaqes Kryesore
    central_widget = QWidget()
    main_layout = QHBoxLayout()

    # Panel 1: Majtas (G-Code Edit & Kontrollet)
    main_layout.addLayout(self.create_left_execution_panel(), stretch=2)

    # Panel 2: Mes (DRO & Feed/Spindle)
    main_layout.addLayout(self.create_middle_dro_panel(), stretch=2)

    # Panel 3: Djathtas (Visualizer 3D & MDI)
    main_layout.addLayout(self.create_right_visualizer_panel(), stretch=4)

    central_widget.setLayout(main_layout)
    self.setCentralWidget(central_widget)

    # Status Bar në fund
    self.status_bar = QStatusBar()
    self.setStatusBar(self.status_bar)

    # Lidhja e butonit Enable
    if hasattr(self, "btn_enable"):
      self.btn_enable.clicked.connect(self.toggle_enable_state)

    # Përditësojmë gjendjen e ndërfaqes për Enable / ESTOP
    self.update_enable_ui_state()

  # -------------------------------------------------------------------------
  # LOGJIKA E ENABLE / DISABLE / ESTOP & OUTPUT PIN 24
  # -------------------------------------------------------------------------
  def _toggle_enable_button_blink(self):
    """Bën pulsimin e kornizës së butonit Enable (Kuq / Gjelbër) kur është në ESTOP."""
    self.blink_state = not self.blink_state
    border_color = "#00FF00" if self.blink_state else "#FF0000"

    if hasattr(self, "btn_enable"):
      self.btn_enable.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2D2D30;
                    color: #FFFFFF;
                    border: 2px solid {border_color};
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    height: 32px;
                }}
                QPushButton:hover {{
                    background-color: #3E3E42;
                }}
            """)

  def update_enable_ui_state(self):
    """Përditëson ndërfaqen sipas gjendjeve Enable/Disable."""
    if self.is_enabled:
      self.blink_timer.stop()

      if hasattr(self, "btn_enable"):
        self.btn_enable.setText("Disable")
        self.btn_enable.setStyleSheet("""
                    QPushButton {
                        background-color: #2D2D30;
                        color: #FFFFFF;
                        border: 2px solid #00FF00;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                        height: 32px;
                    }
                """)

      self.status_bar.showMessage("Connected. ETH-MCI firmware version: 00.58")
      self.set_output_pin_state("Enable", pin_number=24, state=True)

    else:
      if hasattr(self, "btn_enable"):
        self.btn_enable.setText("Enable")

      if not self.blink_timer.isActive():
        self.blink_timer.start()

      self.status_bar.showMessage("ESTOP for reconfiguration.")
      self.set_output_pin_state("Enable", pin_number=24, state=False)

  def toggle_enable_state(self):
    """Shtypja e butonit Enable/Disable."""
    if not self.is_enabled and self.check_hardware_estop():
      QMessageBox.critical(
          self,
          "E-Stop i Shtypur",
          "Nuk mund të aktivizohet makina sepse butoni fizik E-Stop është i"
          " shtypur!\n\nLirojeni butonin E-Stop te makina dhe provoni"
          " përsëri.",
      )
      return

    self.is_enabled = not self.is_enabled
    self.update_enable_ui_state()

  def check_hardware_estop(self) -> bool:
    """Lexon nëse butoni fizik E-Stop (Input Pin 1) është aktiv."""
    if self.motion_controller is not None and hasattr(
        self.motion_controller, "get_input_pin"
    ):
      return self.motion_controller.get_input_pin(1) == 1
    return self.estop_active

  def set_output_pin_state(
      self, signal_name: str, pin_number: int, state: bool
  ):
    """Ndez ose ndal pinit e daljes (Pin 24 për Enable Relay)."""
    print(
        f"[HARDWARE OUTPUT] Signal: {signal_name} | Pin: {pin_number} | State:"
        f" {'HIGH (1)' if state else 'LOW (0)'}"
    )
    if self.motion_controller is not None and hasattr(
        self.motion_controller, "set_output_pin"
    ):
      self.motion_controller.set_output_pin(pin_number, 1 if state else 0)

  # -------------------------------------------------------------------------
  # JOG & MPG DIALOG HANDLERS
  # -------------------------------------------------------------------------
  def action_open_jog_mpg_window(self):
    if self.jog_dialog is None:
      self.jog_dialog = JogMPGDialog(
          config_manager=self.cfg, parent=self
      )

      self.jog_dialog.jog_started.connect(self.handle_jog_start)
      self.jog_dialog.jog_stopped.connect(self.handle_jog_stop)
      self.jog_dialog.jog_mode_changed.connect(self.handle_jog_mode_changed)
      self.jog_dialog.mpg_axis_changed.connect(self.handle_mpg_axis_changed)

    self.jog_dialog.show()
    self.jog_dialog.raise_()
    self.jog_dialog.activateWindow()

  def handle_jog_start(self, axis: str, direction: int):
    """Ekzekutohet kur shtypet një nga butonat e lëvizjes."""
    if self.jog_dialog is None or not self.is_enabled:
      return

    mode = self.jog_dialog.modes[self.jog_dialog.current_mode_index]
    step_size = float(self.jog_dialog.txt_jog_step.text() or 0.01)
    slow_jog = float(self.jog_dialog.txt_slow_jog.text() or 100)

    if axis in self.axis_positions:
      self.axis_positions[axis] += step_size * direction
      self.update_dro_display(axis, self.axis_positions[axis])

    if self.motion_controller is not None and hasattr(
        self.motion_controller, "start_jog"
    ):
      self.motion_controller.start_jog(
          axis, direction, mode, step_size, slow_jog
      )

  def handle_jog_stop(self, axis: str):
    """Ekzekutohet kur lëshohet butoni i lëvizjes."""
    if self.motion_controller is not None and hasattr(
        self.motion_controller, "stop_jog"
    ):
      self.motion_controller.stop_jog(axis)

  def handle_jog_mode_changed(self, mode: str):
    print(f"[JOG MODE] U ndryshua në: {mode}")

  def handle_mpg_axis_changed(self, axis: str):
    print(f"[MPG AXIS] U zgjodh aks: {axis}")

  def update_dro_display(self, axis: str, value: float):
    """Përditëson shfaqjen e koordinatave në UI (DRO)."""
    formatted_val = f"{value:+0.4f}"

    if axis in self.dro_labels:
      self.dro_labels[axis].setText(formatted_val)

    if self.visualizer is not None:
      self.visualizer.update_tool_position(
          self.axis_positions.get("X", 0.0),
          self.axis_positions.get("Y", 0.0),
          self.axis_positions.get("Z", 0.0),
      )

  # -------------------------------------------------------------------------
  # STRUKTURA E MENYSË KRYESORE
  # -------------------------------------------------------------------------
  def create_menu_bar(self):
    menu_bar = self.menuBar()

    # ==================== 1. FILE ====================
    file_menu = menu_bar.addMenu("File")

    act_new = QAction("New...", self)
    act_open = QAction("Open...", self)
    act_open.triggered.connect(self.action_load_gcode)

    act_adv_load = QAction("Enable advanced load options", self)
    act_adv_load.setCheckable(True)
    act_adv_load.setChecked(True)

    act_edit = QAction("Edit...", self)

    file_menu.addAction(act_new)
    file_menu.addAction(act_open)
    file_menu.addAction(act_adv_load)
    file_menu.addAction(act_edit)
    file_menu.addSeparator()

    act_recent = QAction("Recent document", self)
    act_recent.setEnabled(False)
    file_menu.addAction(act_recent)
    file_menu.addSeparator()

    act_exit = QAction("Exit", self)
    act_exit.triggered.connect(self.close)
    file_menu.addAction(act_exit)

    # ==================== 2. CONFIG ====================
    config_menu = menu_bar.addMenu("Config")

    act_motion = QAction("Motion controller...", self)
    act_motion.triggered.connect(self.action_open_motion_controller_dialog)

    act_setup = QAction("Setup...", self)
    act_setup.triggered.connect(self.action_open_setup_dialog)

    act_fixtures = QAction("Fixtures...", self)
    act_tooltable = QAction("Tooltable...", self)
    act_safez = QAction("SafeZ...", self)

    config_menu.addAction(act_motion)
    config_menu.addAction(act_setup)
    config_menu.addAction(act_fixtures)
    config_menu.addAction(act_tooltable)
    config_menu.addAction(act_safez)

    # ==================== 3. VIEW ====================
    view_menu = menu_bar.addMenu("View")

    act_show_normal = QAction("Show normal", self)
    act_show_maximized = QAction("Show maximized", self)
    act_show_maximized.setCheckable(True)
    act_show_maximized.setChecked(True)
    act_fullscreen = QAction("Fullscreen", self)

    win_group = QActionGroup(self)
    win_group.addAction(act_show_normal)
    win_group.addAction(act_show_maximized)
    win_group.addAction(act_fullscreen)

    view_menu.addAction(act_show_normal)
    view_menu.addAction(act_show_maximized)
    view_menu.addAction(act_fullscreen)
    view_menu.addSeparator()

    act_std_screen = QAction("Standard screen", self)
    act_std_screen.setCheckable(True)
    act_std_screen.setChecked(True)
    act_thc_screen = QAction("THC/Plasma screen", self)
    act_thc_screen.setCheckable(True)

    screen_group = QActionGroup(self)
    screen_group.addAction(act_std_screen)
    screen_group.addAction(act_thc_screen)

    view_menu.addAction(act_std_screen)
    view_menu.addAction(act_thc_screen)
    view_menu.addSeparator()

    theme_menu = QMenu("Theme", self)
    theme_menu.addAction("Dark Industrial")
    theme_menu.addAction("Light Classic")
    view_menu.addMenu(theme_menu)

    lang_menu = QMenu("Language", self)
    lang_menu.addAction("English")
    lang_menu.addAction("Shqip")
    view_menu.addMenu(lang_menu)

    view_menu.addSeparator()
    view_menu.addAction("IO Diagnostics")
    act_jog_mpg_window = QAction("Jog & MPG window", self)
    act_jog_mpg_window.triggered.connect(self.action_open_jog_mpg_window)
    view_menu.addAction(act_jog_mpg_window)
    view_menu.addAction("Tool Offsets Window")
    view_menu.addAction("Macro log window")

    # ==================== 4. TOOLS ====================
    tools_menu = menu_bar.addMenu("Tools")

    tools_menu.addAction("Firmware update...")
    tools_menu.addSeparator()

    wizards_menu = QMenu("Wizards", self)
    wizards_menu.addAction("Facing Wizard")
    wizards_menu.addAction("Circle Pocket Wizard")
    tools_menu.addMenu(wizards_menu)

    user_scripts_menu = QMenu("User scripts", self)
    user_scripts_menu.addAction("Run M6 Tool Change")
    tools_menu.addMenu(user_scripts_menu)

    tools_menu.addAction("Edit user scripts...")

    # ==================== 5. ABOUT ====================
    about_menu = menu_bar.addMenu("About")

    act_about = QAction("About Kinetix CNC", self)
    act_about.triggered.connect(self.action_show_about)
    about_menu.addAction(act_about)

    # ==================== WIDGETI NË ANËN E DJATHTË TË MENUBAR ====================
    right_widget = QWidget()
    right_layout = QHBoxLayout(right_widget)
    right_layout.setContentsMargins(5, 0, 10, 0)
    right_layout.setSpacing(8)

    lbl_input = QLabel("Biznesi:")
    lbl_input.setStyleSheet("color: #AAAAAA; font-size: 11px;")

    self.txt_business_name = QLineEdit()
    self.txt_business_name.setPlaceholderText("p.sh. Euro-Model")
    self.txt_business_name.setFixedWidth(130)
    self.txt_business_name.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: #007ACC;
                border: 1px solid #007ACC;
                border-radius: 3px;
                padding: 2px 5px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

    self.txt_business_name.textChanged.connect(self.update_brand_label)

    right_layout.addWidget(lbl_input)
    right_layout.addWidget(self.txt_business_name)

    menu_bar.setCornerWidget(right_widget, Qt.Corner.TopRightCorner)

  def update_brand_label(self, text):
    """Përditëson titullin në Titullin e Dritares (Title Bar) sipas shkrimit në TextBox."""
    text = text.strip()
    if text:
      self.setWindowTitle(
          f"Kinetix CNC - {text} | Profile: [{self.profile_name}]"
      )
    else:
      self.setWindowTitle(
          f"Kinetix CNC - Ether-MCI | Profile: [{self.profile_name}]"
      )

  # -------------------------------------------------------------------------
  # PANELI 1: MAJTAS (G-CODE, RUNTIME STATUS & KONTROLLET)
  # -------------------------------------------------------------------------
  def create_left_execution_panel(self):
    left_layout = QVBoxLayout()
    left_layout.setContentsMargins(0, 0, 0, 0)

    self.txt_gcode = QPlainTextEdit()
    self.txt_gcode.setPlaceholderText("G-Code...")
    left_layout.addWidget(self.txt_gcode, stretch=1)

    status_grid = QGridLayout()

    btn_load = QPushButton("Load...")
    btn_load.clicked.connect(self.action_load_gcode)

    lbl_cur = QLabel("Cur line")
    lbl_time = QLabel("Time")

    self.txt_cur_line = QLineEdit("-")
    self.txt_cur_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.txt_cur_line.setReadOnly(True)

    self.txt_time = QLineEdit("00:00:00")
    self.txt_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.txt_time.setReadOnly(True)

    btn_edit = QPushButton("Edit...")

    status_grid.addWidget(btn_load, 0, 0, 1, 2)
    status_grid.addWidget(lbl_cur, 1, 0, Qt.AlignmentFlag.AlignCenter)
    status_grid.addWidget(lbl_time, 1, 1, Qt.AlignmentFlag.AlignCenter)
    status_grid.addWidget(self.txt_cur_line, 2, 0)
    status_grid.addWidget(self.txt_time, 2, 1)
    status_grid.addWidget(btn_edit, 2, 2)

    left_layout.addLayout(status_grid)

    btn_grid = QGridLayout()

    btn_start = QPushButton("Start")
    btn_start.setStyleSheet(
        "background-color: #28a745; color: white; height: 32px; font-size:"
        " 12px;"
    )

    btn_stop = QPushButton("Stop")
    btn_stop.setStyleSheet(
        "background-color: #b22222; color: white; height: 32px; font-size:"
        " 12px;"
    )

    btn_feedhold = QPushButton("FeedHold")
    btn_feedhold.setStyleSheet(
        "background-color: #17a2b8; color: white; height: 32px;"
    )

    btn_rewind = QPushButton("Rewind")
    btn_rewind.setStyleSheet("height: 32px;")

    self.btn_enable = QPushButton("Enable")

    btn_grid.addWidget(btn_start, 0, 0)
    btn_grid.addWidget(btn_stop, 0, 1)
    btn_grid.addWidget(btn_feedhold, 0, 2)
    btn_grid.addWidget(btn_rewind, 0, 3)
    btn_grid.addWidget(self.btn_enable, 1, 0, 1, 2)

    radio_style = """
            QRadioButton {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 8px;
                border: 2px solid #FFFFFF;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #007ACC;
                border: 2px solid #FFFFFF;
            }
        """

    ind_layout = QVBoxLayout()

    self.rb_tool = QRadioButton("Tool change")
    self.rb_tool.setStyleSheet(radio_style)

    self.rb_coolant = QRadioButton("Coolant")
    self.rb_coolant.setStyleSheet(radio_style)

    self.rb_dwell = QRadioButton("Dwell")
    self.rb_dwell.setStyleSheet(radio_style)

    ind_layout.addWidget(self.rb_tool)
    ind_layout.addWidget(self.rb_coolant)
    ind_layout.addWidget(self.rb_dwell)

    btn_grid.addLayout(ind_layout, 1, 2, 1, 2)

    left_layout.addLayout(btn_grid)
    return left_layout

  # -------------------------------------------------------------------------
  # PANELI 2: MES (DRO & FEED / SPINDLE CONTROLS)
  # -------------------------------------------------------------------------
  def create_middle_dro_panel(self):
    mid_layout = QVBoxLayout()
    mid_layout.setContentsMargins(0, 0, 0, 0)

    dro_box = QGroupBox("DRO (KOORDINATAT)")
    dro_layout = QVBoxLayout()

    axes = ["X", "Y", "Z", "A", "B", "C"]
    colors = ["#FF5555", "#55FF55", "#5599FF", "#FFAA00", "#AA55FF", "#00AAAA"]

    for index, axis in enumerate(axes):
      row_widget = QWidget()
      row_layout = QHBoxLayout(row_widget)
      row_layout.setContentsMargins(0, 1, 0, 1)

      lbl_axis = QLabel(axis)
      lbl_axis.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
      lbl_axis.setStyleSheet(f"color: {colors[index]}; min-width: 15px;")

      lbl_val = QLineEdit("+0.0000")
      lbl_val.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
      lbl_val.setStyleSheet(
          "color: #FFFFFF; background-color: #000000; border: 1px solid"
          " #333;"
      )
      lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
      lbl_val.setReadOnly(True)

      self.dro_labels[axis] = lbl_val

      btn_zero = QPushButton("Z")
      btn_zero.setFixedWidth(25)

      row_layout.addWidget(lbl_axis)
      row_layout.addWidget(lbl_val)
      row_layout.addWidget(btn_zero)

      dro_layout.addWidget(row_widget)
      self.axis_widgets[axis] = row_widget

    dro_btns = QGridLayout()
    dro_btns.addWidget(QPushButton("Machine"), 0, 0)
    dro_btns.addWidget(QPushButton("Zero All"), 0, 1)
    dro_btns.addWidget(QPushButton("GotoZero"), 1, 0)

    btn_ref_all = QPushButton("RefAllHome")
    btn_ref_all.clicked.connect(self.action_ref_all_home)
    dro_btns.addWidget(btn_ref_all, 1, 1)

    dro_layout.addLayout(dro_btns)
    dro_box.setLayout(dro_layout)
    mid_layout.addWidget(dro_box)

    fs_box = QGroupBox("FEED & SPINDLE CONTROL")
    fs_layout = QGridLayout()

    fs_layout.addWidget(
        QLabel("F mm/min"), 0, 0, Qt.AlignmentFlag.AlignCenter
    )
    fs_layout.addWidget(QLabel("S rpm"), 0, 1, Qt.AlignmentFlag.AlignCenter)

    txt_f = QLineEdit("100")
    txt_f.setAlignment(Qt.AlignmentFlag.AlignCenter)
    txt_s = QLineEdit("1000")
    txt_s.setAlignment(Qt.AlignmentFlag.AlignCenter)

    fs_layout.addWidget(txt_f, 1, 0)
    fs_layout.addWidget(txt_s, 1, 1)

    fs_layout.addWidget(QLabel("FRO  100 %"), 2, 0)
    fs_layout.addWidget(QLabel("SRO  100 %"), 2, 1)

    btn_spindle = QPushButton("Spindle\nis OFF")
    btn_spindle.setStyleSheet(
        "background-color: #d35400; color: white; font-weight: bold; height:"
        " 40px;"
    )
    fs_layout.addWidget(btn_spindle, 3, 1)

    fs_box.setLayout(fs_layout)
    mid_layout.addWidget(fs_box)
    mid_layout.addStretch()

    self.update_axis_visibility()
    return mid_layout

  # -------------------------------------------------------------------------
  # PANELI 3: DJATHTAS (VISUALIZER 3D & MDI COMMANDS)
  # -------------------------------------------------------------------------
  def create_right_visualizer_panel(self):
    right_layout = QVBoxLayout()
    right_layout.setContentsMargins(0, 0, 0, 0)

    self.visualizer = GCodeVisualizer3D()
    right_layout.addWidget(self.visualizer, stretch=1)

    views_layout = QHBoxLayout()
    for view_name in ["All", "XY", "ZX", "YZ", "Iso"]:
      btn_v = QPushButton(view_name)
      btn_v.clicked.connect(
          lambda _, m=view_name: self.visualizer.set_view_mode(m)
          if self.visualizer is not None
          else None
      )
      views_layout.addWidget(btn_v)

    btn_soft = QPushButton("Soft\nlimits")
    views_layout.addWidget(btn_soft)
    views_layout.addStretch()
    views_layout.addWidget(QPushButton("JogFollow"))

    right_layout.addLayout(views_layout)

    bottom_bar = QHBoxLayout()
    lbl_mdi = QLabel("MDI:")
    self.txt_mdi = QLineEdit("G0 G17 G91.1")

    bottom_bar.addWidget(lbl_mdi)
    bottom_bar.addWidget(self.txt_mdi, stretch=1)
    right_layout.addLayout(bottom_bar)

    actions_layout = QHBoxLayout()
    actions_layout.addWidget(QPushButton("ATZ"))

    btn_safez = QPushButton("Safe Z...")
    actions_layout.addWidget(btn_safez)

    btn_fixtures = QPushButton("Fixtures...")
    actions_layout.addWidget(btn_fixtures)

    btn_setup = QPushButton("Setup...")
    btn_setup.clicked.connect(self.action_open_setup_dialog)
    actions_layout.addWidget(btn_setup)

    actions_layout.addWidget(QPushButton("ToolOff..."))
    actions_layout.addWidget(QPushButton("Tool table..."))

    right_layout.addLayout(actions_layout)
    return right_layout

  # -------------------------------------------------------------------------
  # LOGJIKA E DUKSHMËRISË SË AKSEVE NGA .INI
  # -------------------------------------------------------------------------
  def update_axis_visibility(self):
    if hasattr(self, "cfg") and hasattr(self, "axis_widgets"):
      status = {}
      if hasattr(self.cfg, "get_axis_enable_status"):
        status = self.cfg.get_axis_enable_status() or {}

      for axis, row_widget in self.axis_widgets.items():
        is_enabled = True

        if axis in status:
          is_enabled = status[axis]
        elif f"Axis_{axis}" in status:
          is_enabled = status[f"Axis_{axis}"]
        elif f"Axis{axis}_Enable" in status:
          is_enabled = status[f"Axis{axis}_Enable"]
        elif hasattr(self.cfg, "get_boolean"):
          is_enabled = self.cfg.get_boolean("Axis", f"Enable_{axis}", True)
        elif hasattr(self.cfg, "get"):
          val = self.cfg.get("Axis", f"Enable_{axis}", "True")
          is_enabled = str(val).strip().lower() in ("true", "1", "yes", "on")

        row_widget.setVisible(bool(is_enabled))

  # -------------------------------------------------------------------------
  # VEPRIMET SHPEJTA (ACTIONS)
  # -------------------------------------------------------------------------
  def action_open_motion_controller_dialog(self):
    current_ip = self.cfg.get_motion_controller_ip()
    dlg = MotionControllerDialog(
        current_controller=self.selected_controller,
        current_ip=current_ip,
        parent=self,
    )

    if dlg.exec() == QDialog.DialogCode.Accepted:
      data = dlg.get_selected_data()

      controller_type = data["type_id"]  # p.sh. "2"
      new_ip_hex = data["ip_hex"]  # p.sh. "C0A801DE"

      controller_name = data["controller_name"]
      display_ip = data["ip_str"]

      self.selected_controller = controller_type

      self.cfg.set_motion_controller_type(controller_type)
      self.cfg.set_motion_controller_ip(new_ip_hex)

      msg = QMessageBox(self)
      msg.setIcon(QMessageBox.Icon.Information)
      msg.setWindowTitle("Konfigurimi u Ruajt")
      msg.setText("U ruajt me sukses!")
      msg.setInformativeText(
          f"Kontrolluesi: {controller_name} (Type={controller_type})\n"
          f"IP Adresa: {display_ip} (IP={new_ip_hex})"
      )
      msg.setStyleSheet("""
                QMessageBox { background-color: #1E1E1E; }
                QMessageBox QLabel { color: #FFFFFF !important; font-size: 13px; }
                QPushButton { background-color: #007ACC; color: white; border-radius: 4px; padding: 5px 15px; }
            """)
      msg.exec()

  def action_open_setup_dialog(self):
    dlg = SetupDialog(self.cfg, parent=self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
      if hasattr(self.cfg, "reload"):
        self.cfg.reload()
      elif hasattr(self.cfg, "load_config"):
        self.cfg.load_config()
      elif hasattr(self.cfg, "read_config"):
        self.cfg.read_config()

      self.update_axis_visibility()

      msg = QMessageBox(self)
      msg.setIcon(QMessageBox.Icon.Information)
      msg.setWindowTitle("Setup")
      msg.setText(
          "Konfigurimet nga dritarja Setup u ruajtën me sukses në"
          f" profilin [{self.profile_name}.ini]!"
      )
      msg.setStyleSheet("""
                QMessageBox { background-color: #1E1E1E; }
                QMessageBox QLabel { color: #FFFFFF !important; font-size: 13px; }
                QPushButton { background-color: #007ACC; color: white; border-radius: 4px; padding: 5px 15px; }
            """)
      msg.exec()

  def action_load_gcode(self):
    file_name, _ = QFileDialog.getOpenFileName(
        self,
        "Hap Skedarin G-Code",
        "",
        "G-Code Files (*.tap *.nc *.gcode *.txt);;All Files (*)",
    )
    if file_name:
      try:
        with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
          content = f.read()
          self.txt_gcode.setPlainText(content)
          if self.visualizer is not None:
            self.visualizer.set_gcode(content)
      except Exception as e:
        QMessageBox.critical(
            self, "Gabim", f"E pamundur të hapet skedari: {str(e)}"
        )

  def action_ref_all_home(self):
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Ref All Home")
    msg.setInformativeText(
        "Po ekzekutohet homing për të gjitha akset e aktivizuara..."
    )
    msg.exec()

  def action_show_about(self):
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Rreth Kinetix CNC")
    msg.setText(
        "<b>Kinetix CNC Controller</b><br>Hardware Support: Ether-MCI"
        f" Controller<br>Profili i Aktivizuar: <b>{self.profile_name}</b><br><br>Zhvilluar"
        " me PySide6 (Qt6)."
    )

    msg.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
            }
            QMessageBox QLabel {
                color: #FFFFFF !important;
                font-size: 13px;
            }
            QPushButton {
                background-color: #007ACC;
                color: #FFFFFF;
                border: 1px solid #005A9E;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
        """)

    msg.exec()


if __name__ == "__main__":
  app = QApplication(sys.argv)

  selector = ProfileSelectorDialog()
  if selector.exec() == QDialog.DialogCode.Accepted:
    selected_prof = selector.selected_profile

    main_win = MainWindow(selected_prof)
    main_win.show()
    sys.exit(app.exec())
  else:
    sys.exit(0)