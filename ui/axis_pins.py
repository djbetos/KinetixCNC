from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class AxisOutputPinsWidget(QWidget):
    """Faqja Axis output pins."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Axis",
            "Enable",
            "Step Pin",
            "Dir Pin",
            "Step ActiveLow",
            "Dir ActiveLow",
        ])

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        note_label = QLabel(
            "NOTE: Spindle step pin is used for PWM output in spindle PWM motor control mode"
        )
        note_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #a0a0a0; margin-top: 5px;"
        )
        layout.addWidget(note_label)

    def load_data(self):
        axes_list = ["X", "Y", "Z", "A", "B", "C", "Spindle"]

        enabled_status = {}
        if self.config_manager and hasattr(
            self.config_manager, "get_axis_enable_status"
        ):
            enabled_status = self.config_manager.get_axis_enable_status()

        defaults = {
            "X": (True, 1, 2, False, False),
            "Y": (True, 3, 4, False, False),
            "Z": (True, 5, 6, False, False),
            "A": (True, 0, 0, False, False),
            "B": (False, 0, 0, False, False),
            "C": (False, 0, 0, False, False),
            "Spindle": (True, 9, 0, False, False),
        }

        self.table.setRowCount(len(axes_list))

        for row, axis_name in enumerate(axes_list):
            def_enable, def_step, def_dir, def_sal, def_dal = defaults[axis_name]

            if self.config_manager:
                raw_enable = self.config_manager.get(
                    "AXIS_ENABLE", axis_name, fallback=str(def_enable)
                )
                is_enabled = raw_enable.lower() in ("true", "1")
            else:
                is_enabled = enabled_status.get(axis_name, def_enable)

            step_pin = def_step
            dir_pin = def_dir
            step_al = def_sal
            dir_al = def_dal

            if self.config_manager:
                section = f"AXIS_{axis_name}"
                step_pin = int(
                    self.config_manager.get(section, "StepPin", fallback=str(def_step))
                )
                dir_pin = int(
                    self.config_manager.get(section, "DirPin", fallback=str(def_dir))
                )
                step_al = (
                    self.config_manager.get(
                        section, "StepActiveLow", fallback=str(def_sal)
                    ).lower()
                    == "true"
                )
                dir_al = (
                    self.config_manager.get(
                        section, "DirActiveLow", fallback=str(def_dal)
                    ).lower()
                    == "true"
                )

            item_axis = QTableWidgetItem(axis_name)
            item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, item_axis)

            chk_enable = QCheckBox()
            chk_enable.setChecked(is_enabled)
            self._add_widget_centered(row, 1, chk_enable)

            spin_step = QSpinBox()
            spin_step.setRange(0, 255)
            spin_step.setValue(step_pin)
            spin_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 2, spin_step)

            spin_dir = QSpinBox()
            spin_dir.setRange(0, 255)
            spin_dir.setValue(dir_pin)
            spin_dir.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 3, spin_dir)

            chk_step_al = QCheckBox()
            chk_step_al.setChecked(step_al)
            self._add_widget_centered(row, 4, chk_step_al)

            chk_dir_al = QCheckBox()
            chk_dir_al.setChecked(dir_al)
            self._add_widget_centered(row, 5, chk_dir_al)

    def _add_widget_centered(self, row: int, col: int, widget: QWidget):
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.addWidget(widget)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, col, container)

    def _get_checkbox_state(self, row: int, col: int) -> bool:
        container = self.table.cellWidget(row, col)
        if container is not None:
            chk = container.findChild(QCheckBox)
            if chk is not None:
                return chk.isChecked()
        return False

    def get_data(self) -> dict:
        data = {}
        axes = ["X", "Y", "Z", "A", "B", "C", "Spindle"]
        for row, axis in enumerate(axes):
            spin_step = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
            spin_dir = cast(Optional[QSpinBox], self.table.cellWidget(row, 3))

            step_val = spin_step.value() if spin_step is not None else 0
            dir_val = spin_dir.value() if spin_dir is not None else 0

            data[axis] = {
                "enable": self._get_checkbox_state(row, 1),
                "step_pin": step_val,
                "dir_pin": dir_val,
                "step_active_low": self._get_checkbox_state(row, 4),
                "dir_active_low": self._get_checkbox_state(row, 5),
            }
        return data

    def save_settings(self):
        if not self.config_manager:
            return

        data = self.get_data()

        for ax in ["X", "Y", "Z", "A", "B", "C"]:
            if ax in data:
                self.config_manager.set(
                    "AXIS_ENABLE", ax, "True" if data[ax]["enable"] else "False"
                )

        for axis, info in data.items():
            section = f"AXIS_{axis}"
            self.config_manager.set(section, "StepPin", str(info["step_pin"]))
            self.config_manager.set(section, "DirPin", str(info["dir_pin"]))
            self.config_manager.set(
                section,
                "StepActiveLow",
                "True" if info["step_active_low"] else "False",
            )
            self.config_manager.set(
                section,
                "DirActiveLow",
                "True" if info["dir_active_low"] else "False",
            )