import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class VelocityGraphWidget(QFrame):
    """Widget i veçantë me QPainter për vizatimin e grafikut të profilut të shpejtësisë."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #252526; border: 1px solid #333333; border-radius: 4px;")
        self.max_vel = 6000.0
        self.max_acc = 200.0

    def set_params(self, vel: float, acc: float):
        self.max_vel = max(vel, 1.0)
        self.max_acc = max(acc, 1.0)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = 45
        margin_bottom = 25
        margin_top = 20
        margin_right = 20

        graph_w = w - margin_left - margin_right
        graph_h = h - margin_bottom - margin_top

        # Vizatimi i rrjetës (Grid lines)
        pen_grid = QPen(QColor("#3A3A3C"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen_grid)

        # Rrjeta horizontale (Velociteti)
        for i in range(5):
            y = margin_top + graph_h - (i * graph_h / 4)
            painter.drawLine(margin_left, int(y), w - margin_right, int(y))

        # Rrjeta vertikale (Koha)
        for i in range(7):
            x = margin_left + (i * graph_w / 6)
            painter.drawLine(int(x), margin_top, int(x), h - margin_bottom)

        # Etiketat e akseve
        painter.setPen(QColor("#CCCCCC"))
        painter.setFont(QFont("Segoe UI", 8))

        # Aksi Y (Vel)
        painter.drawText(10, 15, "Vel")
        for i in range(5):
            val = int((self.max_vel / 4) * i)
            y = margin_top + graph_h - (i * graph_h / 4)
            painter.drawText(5, int(y + 4), f"{val}")

        # Nxitimi: Koha acc (s) = (Vel / 60) / Acc
        t_acc = (self.max_vel / 60.0) / self.max_acc
        t_total = max(t_acc * 4.0, 1.0)

        # Aksi X (sec)
        painter.drawText(w - 25, h - 5, "sec")
        for i in range(7):
            t_val = (t_total / 6) * i
            x = margin_left + (i * graph_w / 6)
            painter.drawText(int(x - 10), h - 8, f"{t_val:.1f}")

        # Vizatimi i lakores së profilut (S-Curve Curve)
        pen_curve = QPen(QColor("#007ACC"), 2)
        if "#" in self.styleSheet():
            pen_curve = QPen(QColor("#10B981"), 2.5)  # Vijë me ngjyrë për kontrast kualitativ

        painter.setPen(pen_curve)

        path = QPainterPath()
        p_start_x = margin_left
        p_start_y = margin_top + graph_h

        path.moveTo(p_start_x, p_start_y)

        # Llogaritja e pikave të lakores
        steps = 100
        for i in range(steps + 1):
            t = (t_total / steps) * i
            if t < t_acc:
                # Faza e Nxitimit (Smooth S-curve acceleration)
                v = self.max_vel * (0.5 - 0.5 * math.cos(math.pi * (t / t_acc)))
            elif t < t_acc * 3.0:
                # Faza e Shpejtësisë Konstante (Flat Top)
                v = self.max_vel
            elif t < t_acc * 4.0:
                # Faza e Nënxitimit (Smooth S-curve deceleration)
                t_dec = t - (t_acc * 3.0)
                v = self.max_vel * (0.5 + 0.5 * math.cos(math.pi * (t_dec / t_acc)))
            else:
                v = 0.0

            x_pos = margin_left + (t / t_total) * graph_w
            y_pos = margin_top + graph_h - (v / self.max_vel) * graph_h
            path.lineTo(x_pos, y_pos)

        painter.drawPath(path)


class MotorProfilesWidget(QWidget):
    """Faqja Motor profiles me kontroll për çdo aks."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_axis = "X"
        self.axes_data = {}

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Pjesa Qendrore: Grafiku dhe Sliders
        left_layout = QVBoxLayout()

        # Grafiku me Slider Vertikal për MaxVel
        graph_container = QHBoxLayout()
        self.graph = VelocityGraphWidget()

        self.slider_vel_v = QSlider(Qt.Orientation.Vertical)
        self.slider_vel_v.setRange(100, 20000)
        self.slider_vel_v.setValue(6000)
        self.slider_vel_v.valueChanged.connect(self.on_slider_v_changed)

        graph_container.addWidget(self.graph, stretch=1)
        graph_container.addWidget(self.slider_vel_v)
        left_layout.addLayout(graph_container)

        # Slider Horizontal për Nxitimin (MaxAcc)
        self.slider_acc_h = QSlider(Qt.Orientation.Horizontal)
        self.slider_acc_h.setRange(10, 2000)
        self.slider_acc_h.setValue(200)
        self.slider_acc_h.valueChanged.connect(self.on_slider_h_changed)
        left_layout.addWidget(self.slider_acc_h)

        # Controls & Input Layout
        inputs_layout = QHBoxLayout()
        inputs_layout.setContentsMargins(0, 10, 0, 0)

        # Steps/mm
        v_steps = QVBoxLayout()
        lbl_steps = QLabel("Steps/mm")
        self.txt_steps = QLineEdit("1000")
        self.txt_steps.textChanged.connect(self.recalculate)
        v_steps.addWidget(lbl_steps)
        v_steps.addWidget(self.txt_steps)

        # MaxVel
        v_vel = QVBoxLayout()
        lbl_vel = QLabel("MaxVel [mm/min]")
        self.txt_vel = QLineEdit("6000")
        self.txt_vel.textChanged.connect(self.on_txt_vel_changed)
        v_vel.addWidget(lbl_vel)
        v_vel.addWidget(self.txt_vel)

        # MaxAcc
        v_acc = QVBoxLayout()
        lbl_acc = QLabel("MaxAcc [mm/s2]")
        self.txt_acc = QLineEdit("200")
        self.txt_acc.textChanged.connect(self.on_txt_acc_changed)
        v_acc.addWidget(lbl_acc)
        v_acc.addWidget(self.txt_acc)

        # Acceleration Time Label Result
        v_time = QVBoxLayout()
        lbl_time_title = QLabel("Acceleration time")
        self.lbl_acc_time = QLabel("0.785 s")
        self.lbl_acc_time.setStyleSheet(
            "background-color: #2D2D30; border: 1px solid #3F3F46; "
            "border-radius: 3px; padding: 4px; font-weight: bold; color: #FFFFFF;"
        )
        self.lbl_acc_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_time.addWidget(lbl_time_title)
        v_time.addWidget(self.lbl_acc_time)

        inputs_layout.addLayout(v_steps)
        inputs_layout.addLayout(v_vel)
        inputs_layout.addLayout(v_acc)
        inputs_layout.addStretch()
        inputs_layout.addLayout(v_time)

        left_layout.addLayout(inputs_layout)
        main_layout.addLayout(left_layout, stretch=1)

        # 2. Pjesa Djathtas: Butonat e Akseve
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)

        self.axis_group = QButtonGroup(self)
        self.axis_buttons = {}

        axes = ["X", "Y", "Z", "A", "B", "C", "Spindle"]
        for ax in axes:
            btn = QPushButton(ax)
            btn.setCheckable(True)
            btn.setFixedWidth(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D30;
                    color: #FFFFFF;
                    border: 1px solid #3F3F46;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #007ACC;
                    border-color: #007ACC;
                }
                QPushButton:hover:!checked {
                    background-color: #3E3E42;
                }
            """)
            self.axis_group.addButton(btn)
            self.axis_buttons[ax] = btn
            right_layout.addWidget(btn)

        self.axis_buttons["X"].setChecked(True)
        self.axis_group.buttonClicked.connect(self.on_axis_changed)

        right_layout.addStretch()
        main_layout.addLayout(right_layout)

    def load_data(self):
        axes = ["X", "Y", "Z", "A", "B", "C", "Spindle"]
        defaults = {
            "X": (1000.0, 6000.0, 200.0),
            "Y": (1000.0, 6000.0, 200.0),
            "Z": (1000.0, 3000.0, 150.0),
            "A": (100.0, 3600.0, 100.0),
            "B": (100.0, 3600.0, 100.0),
            "C": (100.0, 3600.0, 100.0),
            "Spindle": (1.0, 12000.0, 500.0),
        }

        for ax in axes:
            def_steps, def_vel, def_acc = defaults[ax]
            if self.config_manager:
                sec = f"AXIS_{ax}"
                steps = float(self.config_manager.get(sec, "StepsPerUnit", fallback=str(def_steps)))
                vel = float(self.config_manager.get(sec, "MaxVelocity", fallback=str(def_vel)))
                acc = float(self.config_manager.get(sec, "MaxAcceleration", fallback=str(def_acc)))
            else:
                steps, vel, acc = def_steps, def_vel, def_acc

            self.axes_data[ax] = {"steps": steps, "vel": vel, "acc": acc}

        self.update_ui_for_axis("X")

    def update_ui_for_axis(self, axis_name: str):
        self.current_axis = axis_name
        data = self.axes_data.get(axis_name, {"steps": 1000.0, "vel": 6000.0, "acc": 200.0})

        self.txt_steps.setText(f"{data['steps']:.2f}".rstrip('0').rstrip('.'))
        self.txt_vel.setText(f"{data['vel']:.0f}")
        self.txt_acc.setText(f"{data['acc']:.0f}")

        self.slider_vel_v.setValue(int(data["vel"]))
        self.slider_acc_h.setValue(int(data["acc"]))

        self.recalculate()

    def on_axis_changed(self, button: QPushButton):
        # Ruajmë të dhënat e aksit aktual para ndërrimit
        self.save_current_axis_data()
        self.update_ui_for_axis(button.text())

    def save_current_axis_data(self):
        try:
            steps = float(self.txt_steps.text())
            vel = float(self.txt_vel.text())
            acc = float(self.txt_acc.text())
            self.axes_data[self.current_axis] = {"steps": steps, "vel": vel, "acc": acc}
        except ValueError:
            pass

    def on_slider_v_changed(self, val: int):
        self.txt_vel.setText(str(val))
        self.recalculate()

    def on_slider_h_changed(self, val: int):
        self.txt_acc.setText(str(val))
        self.recalculate()

    def on_txt_vel_changed(self, text: str):
        try:
            val = int(float(text))
            self.slider_vel_v.setValue(val)
        except ValueError:
            pass
        self.recalculate()

    def on_txt_acc_changed(self, text: str):
        try:
            val = int(float(text))
            self.slider_acc_h.setValue(val)
        except ValueError:
            pass
        self.recalculate()

    def recalculate(self):
        try:
            vel = float(self.txt_vel.text())
            acc = float(self.txt_acc.text())
            if acc > 0:
                # Acceleration time = (Velocity / 60) / Acceleration
                t_acc = (vel / 60.0) / acc
                self.lbl_acc_time.setText(f"{t_acc:.3f} s")
            else:
                self.lbl_acc_time.setText("0.000 s")

            self.graph.set_params(vel, acc)
        except ValueError:
            pass

    def save_settings(self):
        if not self.config_manager:
            return

        self.save_current_axis_data()

        for ax, data in self.axes_data.items():
            sec = f"AXIS_{ax}"
            self.config_manager.set(sec, "StepsPerUnit", str(data["steps"]))
            self.config_manager.set(sec, "MaxVelocity", str(data["vel"]))
            self.config_manager.set(sec, "MaxAcceleration", str(data["acc"]))