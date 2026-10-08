import sys
from typing import Optional, cast
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QStackedWidget, QWidget, QLabel, QLineEdit, QGroupBox, QRadioButton,
    QCheckBox, QComboBox, QPushButton, QFrame, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt


class GeneralSettingsWidget(QWidget):
    """Faqja General Settings."""
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 1. G-code init string
        lbl_gcode = QLabel("G-code init string:")
        self.txt_gcode_init = QLineEdit("G17 G64 G49 G40")
        
        main_layout.addWidget(lbl_gcode)
        main_layout.addWidget(self.txt_gcode_init)

        # 2. Middle Row: Tool change (M6) & Laser options
        mid_layout = QHBoxLayout()

        # Tool change Group
        group_tool = QGroupBox("Tool change (M6)")
        layout_tool = QVBoxLayout()

        self.rb_ignore_tc = QRadioButton("Ignore tool change")
        self.rb_ignore_tc.setChecked(True)
        self.rb_stop_tc = QRadioButton("Stop and wait for START")

        # Location X, Y, Z layout
        pos_layout = QHBoxLayout()
        self.txt_x = QLineEdit("0")
        self.txt_y = QLineEdit("0")
        self.txt_z = QLineEdit("0")
        for txt in (self.txt_x, self.txt_y, self.txt_z):
            txt.setFixedWidth(50)

        pos_layout.addWidget(QLabel("X"))
        pos_layout.addWidget(self.txt_x)
        pos_layout.addWidget(QLabel("Y"))
        pos_layout.addWidget(self.txt_y)
        pos_layout.addWidget(QLabel("Z"))
        pos_layout.addWidget(self.txt_z)
        pos_layout.addStretch()

        self.rb_goto_loc = QRadioButton("Goto location (machine coord.)")
        self.rb_atc = QRadioButton("Automatic Tool Changer")

        layout_tool.addWidget(self.rb_ignore_tc)
        layout_tool.addWidget(self.rb_stop_tc)
        layout_tool.addLayout(pos_layout)
        layout_tool.addWidget(self.rb_goto_loc)
        layout_tool.addWidget(self.rb_atc)
        group_tool.setLayout(layout_tool)

        # Laser options Group
        group_laser = QGroupBox("Laser options")
        layout_laser = QVBoxLayout()
        self.chk_laser = QCheckBox("Gray level laser engraving (A axis controls PWM duty cycle)")
        layout_laser.addWidget(self.chk_laser)
        layout_laser.addStretch()
        group_laser.setLayout(layout_laser)

        mid_layout.addWidget(group_tool, stretch=1)
        mid_layout.addWidget(group_laser, stretch=1)
        main_layout.addLayout(mid_layout)

        # 3. Bottom Grid Settings
        grid_layout = QGridLayout()

        self.chk_g04 = QCheckBox("G04 dwell time in seconds")
        self.chk_ignore_gcode = QCheckBox("Ignore unsupported G codes")
        self.chk_auto_limits = QCheckBox("Auto limits override")
        self.chk_auto_limits.setChecked(True)

        lbl_buffer = QLabel("Motion buffer size:")
        self.combo_buffer = QComboBox()
        self.combo_buffer.addItems(["Normal (default)", "Small", "Large"])

        lbl_freq = QLabel("Maximum step frequency:")
        self.combo_freq = QComboBox()
        self.combo_freq.addItems(["100 kHz", "200 kHz", "400 kHz", "500 kHz"])
        self.combo_freq.setCurrentText("200 kHz")

        self.chk_probe_limit = QCheckBox("Probe as limit")
        self.chk_dme = QCheckBox("Enable DME server")

        grid_layout.addWidget(self.chk_g04, 0, 0)
        grid_layout.addWidget(lbl_buffer, 0, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.combo_buffer, 0, 2)

        grid_layout.addWidget(self.chk_ignore_gcode, 1, 0)
        grid_layout.addWidget(lbl_freq, 1, 1, Qt.AlignmentFlag.AlignRight)
        grid_layout.addWidget(self.combo_freq, 1, 2)

        grid_layout.addWidget(self.chk_auto_limits, 2, 0)
        grid_layout.addWidget(self.chk_probe_limit, 2, 2)

        grid_layout.addWidget(self.chk_dme, 3, 2)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

    def load_settings(self):
        """Lexon cilësimet nga config manager nëse ekziston."""
        if not self.config_manager:
            return
        gcode_init = self.config_manager.get("GENERAL", "GCodeInit", fallback="G17 G64 G49 G40")
        self.txt_gcode_init.setText(gcode_init)

    def save_settings(self):
        """Ruan cilësimet e General Settings te config manager."""
        if not self.config_manager:
            return
        self.config_manager.set("GENERAL", "GCodeInit", self.txt_gcode_init.text())


class AxisOutputPinsWidget(QWidget):
    """Faqja Axis output pins."""
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Krijimi i Tabelës
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Axis", "Enable", "Step Pin", "Dir Pin", "Step ActiveLow", "Dir ActiveLow"
        ])
        
        # Stili i kokës së tabelës (Header)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Shënimi në fund (NOTE)
        note_label = QLabel("NOTE: Spindle step pin is used for PWM output in spindle PWM motor control mode")
        note_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #a0a0a0; margin-top: 10px;")
        layout.addWidget(note_label)

    def load_data(self):
        """Lexon të dhënat nga ConfigManager ose përdor vlerat default."""
        axes_list = ["X", "Y", "Z", "A", "B", "C", "Spindle"]
        
        # Merr statusin aktual të akseve nga ConfigManager
        enabled_status = {}
        if self.config_manager and hasattr(self.config_manager, "get_axis_enable_status"):
            enabled_status = self.config_manager.get_axis_enable_status()

        # Vlerat bazë për kunjat (Pins)
        defaults = {
            "X": (True, 1, 2, False, False),
            "Y": (True, 3, 4, False, False),
            "Z": (True, 5, 6, False, False),
            "A": (True, 0, 0, False, False),
            "B": (True, 0, 0, False, False),
            "C": (True, 0, 0, False, False),
            "Spindle": (True, 9, 0, False, False),
        }

        self.table.setRowCount(len(axes_list))

        for row, axis_name in enumerate(axes_list):
            def_enable, def_step, def_dir, def_sal, def_dal = defaults[axis_name]
            
            # Nëse ekziston statusi në config_manager, përdor atë për Enable
            is_enabled = enabled_status.get(axis_name, def_enable)
            
            # Lexo kunjat nga config nëse ekzistojnë
            step_pin = def_step
            dir_pin = def_dir
            if self.config_manager:
                step_pin = int(self.config_manager.get(f"AXIS_{axis_name}", "StepPin", fallback=str(def_step)))
                dir_pin = int(self.config_manager.get(f"AXIS_{axis_name}", "DirPin", fallback=str(def_dir)))

            # 0. Axis Name (Read Only)
            item_axis = QTableWidgetItem(axis_name)
            item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, item_axis)

            # 1. Enable (CheckBox)
            chk_enable = QCheckBox()
            chk_enable.setChecked(is_enabled)
            self._add_widget_centered(row, 1, chk_enable)

            # 2. Step Pin (SpinBox)
            spin_step = QSpinBox()
            spin_step.setRange(0, 255)
            spin_step.setValue(step_pin)
            spin_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 2, spin_step)

            # 3. Dir Pin (SpinBox)
            spin_dir = QSpinBox()
            spin_dir.setRange(0, 255)
            spin_dir.setValue(dir_pin)
            spin_dir.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 3, spin_dir)

            # 4. Step ActiveLow (CheckBox)
            chk_step_al = QCheckBox()
            chk_step_al.setChecked(def_sal)
            self._add_widget_centered(row, 4, chk_step_al)

            # 5. Dir ActiveLow (CheckBox)
            chk_dir_al = QCheckBox()
            chk_dir_al.setChecked(def_dal)
            self._add_widget_centered(row, 5, chk_dir_al)

    def _add_widget_centered(self, row: int, col: int, widget: QWidget):
        """Ndihmon në qendrimin e CheckBox-eve brenda qelizës së tabelës"""
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.addWidget(widget)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, col, container)

    def _get_checkbox_state(self, row: int, col: int) -> bool:
        """Ndihmës për marrjen e sigurt të gjendjes së QCheckBox brenda kontejnerit"""
        container = self.table.cellWidget(row, col)
        if container is not None:
            chk = container.findChild(QCheckBox)
            if chk is not None:
                return chk.isChecked()
        return False

    def get_data(self) -> dict:
        """Merr të dhënat e konfiguruara nga tabela"""
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
        """Ruan të gjitha të dhënat e tabelës te ConfigManager."""
        if not self.config_manager:
            return

        data = self.get_data()
        
        # 1. Ruan statusin e Enable për akset (X, Y, Z, A, B, C)
        axis_enable_map = {ax: data[ax]["enable"] for ax in ["X", "Y", "Z", "A", "B", "C"] if ax in data}
        if hasattr(self.config_manager, "set_axis_enable_status"):
            self.config_manager.set_axis_enable_status(axis_enable_map)

        # 2. Ruan Step/Dir kunjat për secilin aks te seksionet përkatëse
        for axis, info in data.items():
            self.config_manager.set(f"AXIS_{axis}", "StepPin", str(info["step_pin"]))
            self.config_manager.set(f"AXIS_{axis}", "DirPin", str(info["dir_pin"]))
            self.config_manager.set(f"AXIS_{axis}", "StepActiveLow", str(info["step_active_low"]))
            self.config_manager.set(f"AXIS_{axis}", "DirActiveLow", str(info["dir_active_low"]))


class SetupDialog(QDialog):
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Setup")
        self.resize(900, 600)

        # QSS Stili sipas pamjes Dark të Controller-it
        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QTreeWidget { background-color: #252526; color: #CCCCCC; border: 1px solid #333333; }
            QTreeWidget::item:selected { background-color: #007ACC; color: white; }
            QGroupBox { border: 1px solid #333333; border-radius: 4px; margin-top: 10px; font-weight: bold; color: #007ACC; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QLineEdit, QComboBox { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 3px; padding: 4px; }
            QPushButton { background-color: #2D2D30; color: #FFFFFF; border: 1px solid #3F3F46; border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #007ACC; border-color: #007ACC; }
            QCheckBox, QRadioButton, QLabel { color: #CCCCCC; }
            QTableWidget { background-color: #252526; color: #FFFFFF; gridline-color: #333333; border: 1px solid #333333; }
            QHeaderView::section { background-color: #2D2D30; color: #FFFFFF; padding: 4px; border: 1px solid #333333; }
        """)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()

        # Pemët e navigimit majtas
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(200)

        # Ndërtimi i strukturës së pemës
        item_gen = QTreeWidgetItem(self.tree, ["General settings"])
        
        item_axis = QTreeWidgetItem(self.tree, ["Axis setup"])
        item_axis.addChildren([
            QTreeWidgetItem(["Axis output pins"]),
            QTreeWidgetItem(["Motor profiles"]),
            QTreeWidgetItem(["Homing/Limits"]),
            QTreeWidgetItem(["Slave axis"]),
            QTreeWidgetItem(["Backlash compens."]),
            QTreeWidgetItem(["Eth-mc advanced"])
        ])
        item_axis.setExpanded(True)

        self.tree.addTopLevelItem(QTreeWidgetItem(["Input signals"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Output signals"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Encoders & MPGs"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Motion planner"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Spindle & Coolant"]))

        item_thc = QTreeWidgetItem(self.tree, ["THC setup"])
        item_thc.addChildren([
            QTreeWidgetItem(["General THC"]),
            QTreeWidgetItem(["Internal THC"])
        ])
        item_thc.setExpanded(True)

        self.tree.addTopLevelItem(QTreeWidgetItem(["Button scripts"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["External buttons"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Persist options"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["UI options"]))

        content_layout.addWidget(self.tree)

        # Stacked Widget për të ndërruar faqet në të djathtë
        self.stacked_widget = QStackedWidget()
        
        # Faqja 0: General Settings
        self.general_page = GeneralSettingsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.general_page)

        # Faqja 1: Axis Output Pins
        self.axis_pins_page = AxisOutputPinsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.axis_pins_page)

        # Faqja 2: Placeholder për kategoritë e tjera
        self.placeholder_page = QWidget()
        ph_layout = QVBoxLayout(self.placeholder_page)
        self.lbl_placeholder = QLabel("Konfigurimi për këtë seksion do të shtohet së shpejti.")
        self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(self.lbl_placeholder)
        
        self.stacked_widget.addWidget(self.placeholder_page)

        content_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addLayout(content_layout)

        # Paneli poshtë: Import / OK / Cancel
        bottom_layout = QHBoxLayout()
        btn_import = QPushButton("Import from profile...")
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        bottom_layout.addWidget(btn_import)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_ok)
        bottom_layout.addWidget(btn_cancel)

        root_layout.addLayout(bottom_layout)

        # Lidhim klikimin në pemë me ndërrimin e faqeve
        self.tree.currentItemChanged.connect(self.on_tree_selection_changed)
        self.tree.setCurrentItem(item_gen)

    def on_tree_selection_changed(self, current, previous):
        if not current:
            return
        text = current.text(0)
        if text == "General settings":
            self.stacked_widget.setCurrentIndex(0)
        elif text == "Axis output pins":
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.lbl_placeholder.setText(f"Seksioni: [{text}] - Në proces zhvillimi")
            self.stacked_widget.setCurrentIndex(2)

    def accept(self):
        """Thirret automatikisht kur përdoruesi klikon butonin OK."""
        # 1. Ruan cilësimet nga General Settings
        self.general_page.save_settings()

        # 2. Ruan të gjitha të dhënat e akseve te ConfigManager
        self.axis_pins_page.save_settings()

        # 3. Ruan fizikisht skedarin .ini në disk
        if self.config_manager and hasattr(self.config_manager, "save_config"):
            self.config_manager.save_config()

        super().accept()