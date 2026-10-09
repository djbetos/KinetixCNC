import sys
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LEDIndicator(QWidget):
  """Një indikator LED vizual me ngjyrë të gjelbër (On) / të hirtë (Off)."""

  def __init__(self, active=False, parent=None):
    super().__init__(parent)
    self._active = active
    self.setFixedSize(14, 14)

  def set_active(self, active: bool):
    self._active = active
    self.update()

  def is_active(self) -> bool:
    return self._active

  def paintEvent(self, event):
    from PySide6.QtGui import QColor, QPainter, QRadialGradient

    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    color_center = (
        QColor("#00FF00") if self._active else QColor("#555555")
    )  # E gjelbër / E hirtë
    color_edge = QColor("#008800") if self._active else QColor("#222222")

    gradient = QRadialGradient(7, 7, 7)
    gradient.setColorAt(0, color_center)
    gradient.setColorAt(1, color_edge)

    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(1, 1, 12, 12)


class JogMPGDialog(QDialog):
  # Sinjalet për kontrollin e modalitetit dhe akseve
  jog_mode_changed = Signal(str)  # "Cont", "Step", "MPG"
  mpg_axis_changed = Signal(str)  # "X", "Y", "Z", "A", "B", "C"

  # Sinjalet për kontrollin manual të lëvizjes
  jog_started = Signal(str, int)  # axis, direction (+1/-1)
  jog_stopped = Signal(str)  # axis

  def __init__(self, config_manager=None, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager
    self.setWindowTitle("Jog & MPG")
    self.setFixedSize(340, 560)

    # Indekset e gjendjeve aktuale
    self.current_mode_index = 0  # 0: Cont., 1: Step, 2: MPG
    self.current_axis_index = 0  # 0: X, 1: Y, 2: Z, 3: A, 4: B, 5: C

    self.modes = ["Cont.", "Step", "MPG"]
    self.axes = ["X", "Y", "Z", "A", "B", "C"]

    # QSS Stili i errët
    self.setStyleSheet("""
            QDialog {
                background-color: #2A2A2A;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #444444;
                border-radius: 4px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 12px;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #555555;
                font-size: 16px;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: #FFFFFF;
                border: 1px solid #666666;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
                border-color: #888888;
            }
            QPushButton:pressed {
                background-color: #007ACC;
                border-color: #005A9E;
            }
        """)

    self.init_ui()

  def init_ui(self):
    main_layout = QVBoxLayout(self)
    main_layout.setSpacing(8)
    main_layout.setContentsMargins(10, 10, 10, 10)

    # =========================================================================
    # 1. JOG MODE GROUPBOX (Cont. / Step / MPG)
    # =========================================================================
    gb_mode = QGroupBox("Jog mode")
    lay_mode = QHBoxLayout(gb_mode)
    lay_mode.setContentsMargins(10, 12, 10, 8)

    self.btn_set_mode = QPushButton("Set")
    self.btn_set_mode.setFixedSize(65, 32)
    self.btn_set_mode.clicked.connect(self.cycle_jog_mode)

    self.mode_leds = {}
    lay_mode.addWidget(self.btn_set_mode)
    lay_mode.addStretch()

    for idx, mode_name in enumerate(self.modes):
      box, led = self._create_led_option(mode_name, active=(idx == 0))
      self.mode_leds[mode_name] = led
      lay_mode.addLayout(box)
      if idx < len(self.modes) - 1:
        lay_mode.addStretch()

    main_layout.addWidget(gb_mode)

    # =========================================================================
    # 2. INPUT FIELDS (Jog step, Slow jog %, MPG max speed %)
    # =========================================================================
    grid_inputs = QGridLayout()
    grid_inputs.setSpacing(6)

    lbl_step = QLabel("Jog step [mm]")
    lbl_step.setStyleSheet(
        "background-color: #808080; color: #000; font-weight: bold; padding:"
        " 4px;"
    )
    lbl_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.txt_jog_step = QLineEdit("0.0100")
    self.txt_jog_step.setAlignment(Qt.AlignmentFlag.AlignCenter)

    lbl_slow = QLabel("Slow jog [%]")
    lbl_slow.setStyleSheet(
        "background-color: #808080; color: #000; font-weight: bold; padding:"
        " 4px;"
    )
    lbl_slow.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.txt_slow_jog = QLineEdit("1")
    self.txt_slow_jog.setAlignment(Qt.AlignmentFlag.AlignCenter)

    lbl_mpg_speed = QLabel("MPG max speed [%]")
    lbl_mpg_speed.setStyleSheet(
        "background-color: #808080; color: #000; font-weight: bold; padding:"
        " 4px;"
    )
    lbl_mpg_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.txt_mpg_speed = QLineEdit("10")
    self.txt_mpg_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)

    grid_inputs.addWidget(lbl_step, 0, 0)
    grid_inputs.addWidget(self.txt_jog_step, 1, 0)
    grid_inputs.addWidget(lbl_slow, 0, 1)
    grid_inputs.addWidget(self.txt_slow_jog, 1, 1)

    grid_inputs.addWidget(lbl_mpg_speed, 2, 0)
    grid_inputs.addWidget(self.txt_mpg_speed, 2, 1)

    main_layout.addLayout(grid_inputs)

    # =========================================================================
    # 3. MPG AXIS GROUPBOX (Për 6 Akse: X, Y, Z, A, B, C)
    # =========================================================================
    gb_mpg_axis = QGroupBox("MPG axis")
    lay_mpg = QHBoxLayout(gb_mpg_axis)
    lay_mpg.setContentsMargins(10, 12, 10, 8)

    self.btn_mpg1 = QPushButton("MPG1")
    self.btn_mpg1.setFixedSize(65, 32)
    self.btn_mpg1.clicked.connect(self.cycle_mpg_axis)

    lay_mpg.addWidget(self.btn_mpg1)
    lay_mpg.addStretch()

    self.mpg_leds = {}
    for idx, axis in enumerate(self.axes):
      box, led = self._create_led_option(axis, active=(idx == 0))
      self.mpg_leds[axis] = led
      lay_mpg.addLayout(box)
      if idx < len(self.axes) - 1:
        lay_mpg.addStretch()

    main_layout.addWidget(gb_mpg_axis)

    # =========================================================================
    # 4. JOG CONTROL BUTTONS (X, Y, Z, A, B, C)
    # =========================================================================
    gb_controls = QGroupBox("Jog control buttons")
    grid_ctrl = QGridLayout(gb_controls)
    grid_ctrl.setSpacing(6)
    grid_ctrl.setContentsMargins(8, 12, 8, 12)

    self.btn_x_plus = QPushButton("X+")
    self.btn_x_minus = QPushButton("X-")
    self.btn_y_plus = QPushButton("Y+")
    self.btn_y_minus = QPushButton("Y-")
    self.btn_z_plus = QPushButton("Z+")
    self.btn_z_minus = QPushButton("Z-")

    self.btn_a_plus = QPushButton("A+")
    self.btn_a_minus = QPushButton("A-")
    self.btn_b_plus = QPushButton("B+")
    self.btn_b_minus = QPushButton("B-")
    self.btn_c_plus = QPushButton("C+")
    self.btn_c_minus = QPushButton("C-")

    all_btns = [
        self.btn_x_plus,
        self.btn_x_minus,
        self.btn_y_plus,
        self.btn_y_minus,
        self.btn_z_plus,
        self.btn_z_minus,
        self.btn_a_plus,
        self.btn_a_minus,
        self.btn_b_plus,
        self.btn_b_minus,
        self.btn_c_plus,
        self.btn_c_minus,
    ]

    for btn in all_btns:
      btn.setFixedSize(45, 36)

    # Rreshtimi i X, Y, Z dhe A, B, C
    grid_ctrl.addWidget(self.btn_y_plus, 0, 1)
    grid_ctrl.addWidget(self.btn_x_minus, 1, 0)
    grid_ctrl.addWidget(self.btn_x_plus, 1, 2)
    grid_ctrl.addWidget(self.btn_y_minus, 2, 1)

    grid_ctrl.addWidget(self.btn_z_plus, 0, 3)
    grid_ctrl.addWidget(self.btn_z_minus, 2, 3)

    grid_ctrl.addWidget(self.btn_a_plus, 0, 4)
    grid_ctrl.addWidget(self.btn_a_minus, 0, 5)
    grid_ctrl.addWidget(self.btn_b_plus, 1, 4)
    grid_ctrl.addWidget(self.btn_b_minus, 1, 5)
    grid_ctrl.addWidget(self.btn_c_plus, 2, 4)
    grid_ctrl.addWidget(self.btn_c_minus, 2, 5)

    # Lidhja e sinjaleve
    self._setup_button_signals(self.btn_x_plus, "X", 1)
    self._setup_button_signals(self.btn_x_minus, "X", -1)
    self._setup_button_signals(self.btn_y_plus, "Y", 1)
    self._setup_button_signals(self.btn_y_minus, "Y", -1)
    self._setup_button_signals(self.btn_z_plus, "Z", 1)
    self._setup_button_signals(self.btn_z_minus, "Z", -1)

    self._setup_button_signals(self.btn_a_plus, "A", 1)
    self._setup_button_signals(self.btn_a_minus, "A", -1)
    self._setup_button_signals(self.btn_b_plus, "B", 1)
    self._setup_button_signals(self.btn_b_minus, "B", -1)
    self._setup_button_signals(self.btn_c_plus, "C", 1)
    self._setup_button_signals(self.btn_c_minus, "C", -1)

    main_layout.addWidget(gb_controls)

  # =========================================================================
  # LOGJIKA E NDËRRIMIT CIKLIK TË MODE DHE AXIS
  # =========================================================================
  def cycle_jog_mode(self):
    """Ndrron pozicionin nga Cont.

    -> Step -> MPG -> Cont.
    """
    self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
    selected_mode = self.modes[self.current_mode_index]

    # Azhornon LED-et
    for mode_name, led in self.mode_leds.items():
      led.set_active(mode_name == selected_mode)

    # Emeton sinjalin te programi kryesor
    self.jog_mode_changed.emit(selected_mode)

  def cycle_mpg_axis(self):
    """Ndrron aksin nga X -> Y -> Z -> A -> B -> C -> X."""
    self.current_axis_index = (self.current_axis_index + 1) % len(self.axes)
    selected_axis = self.axes[self.current_axis_index]

    # Azhornon LED-et
    for axis_name, led in self.mpg_leds.items():
      led.set_active(axis_name == selected_axis)

    # Emeton sinjalin te programi kryesor
    self.mpg_axis_changed.emit(selected_axis)

  def _create_led_option(self, label_text: str, active: bool = False) -> tuple:
    box = QVBoxLayout()
    box.setSpacing(4)
    box.setAlignment(Qt.AlignmentFlag.AlignCenter)

    lbl = QLabel(label_text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

    led = LEDIndicator(active=active)

    box.addWidget(lbl)
    box.addWidget(led, alignment=Qt.AlignmentFlag.AlignCenter)
    return box, led

  def _setup_button_signals(
      self, button: QPushButton, axis: str, direction: int
  ):
    button.pressed.connect(lambda: self.jog_started.emit(axis, direction))
    button.released.connect(lambda: self.jog_stopped.emit(axis))