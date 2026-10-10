from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Importimi i faqeve individuale nga modulja 'ui'
from ui.axis_pins import AxisOutputPinsWidget
from ui.general_settings import GeneralSettingsWidget
from ui.input_signals import InputSignalsWidget
from ui.output_signals import OutputSignalsWidget
from ui.encoders_mpgs import EncodersMPGsWidget
from ui.motor_profiles import MotorProfilesWidget
from ui.homing_limits import HomingLimitsWidget
from ui.slave_axis import SlaveAxisWidget
from ui.backlash_comp import BacklashCompWidget
from ui.eth_mc_advanced import EthMcAdvancedWidget
from ui.motion_planner import MotionPlannerWidget
from ui.spindle_coolant import SpindleCoolantWidget
from ui.general_thc import GeneralThcWidget
from ui.internal_thc import InternalThcWidget
from ui.button_scripts import ButtonScriptsWidget
from ui.external_buttons import ExternalButtonsWidget
from ui.persist_options import PersistOptionsWidget
from ui.ui_options import UiOptionsWidget
from ui.fixtures_dialog import FixturesDialog

class SetupDialog(QDialog):

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Setup")
        self.resize(900, 600)

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
            
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #888888; border-radius: 3px;
                background-color: #252526;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #FFFFFF; background-color: #3E3E42;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC; border: 2px solid #007ACC;
            }
        """)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Pema e navigimit majtas
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(200)

        item_gen = QTreeWidgetItem(self.tree, ["General settings"])

        item_axis = QTreeWidgetItem(self.tree, ["Axis setup"])
        item_axis.addChildren([
            QTreeWidgetItem(["Axis output pins"]),
            QTreeWidgetItem(["Motor profiles"]),
            QTreeWidgetItem(["Homing/Limits"]),
            QTreeWidgetItem(["Slave axis"]),
            QTreeWidgetItem(["Backlash compens."]),
            QTreeWidgetItem(["Eth-mc advanced"]),
        ])
        item_axis.setExpanded(True)

        item_inputs = QTreeWidgetItem(self.tree, ["Input signals"])
        self.tree.addTopLevelItem(item_inputs)

        item_outputs = QTreeWidgetItem(self.tree, ["Output signals"])
        self.tree.addTopLevelItem(item_outputs)

        self.tree.addTopLevelItem(QTreeWidgetItem(["Encoders & MPGs"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Motion planner"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Spindle & Coolant"]))

        item_thc = QTreeWidgetItem(self.tree, ["THC setup"])
        item_thc.addChildren(
            [QTreeWidgetItem(["General THC"]), QTreeWidgetItem(["Internal THC"])]
        )
        item_thc.setExpanded(True)

        self.tree.addTopLevelItem(QTreeWidgetItem(["Button scripts"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["External buttons"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["Persist options"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["UI options"]))

        content_layout.addWidget(self.tree)

        # Stacked Widget për kontrollin e faqeve
        self.stacked_widget = QStackedWidget()

        # Index 0: General Settings
        self.general_page = GeneralSettingsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.general_page)

        # Index 1: Axis Output Pins
        self.axis_pins_page = AxisOutputPinsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.axis_pins_page)

        # Index 2: Input Signals
        self.input_signals_page = InputSignalsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.input_signals_page)

        # Index 3: Output Signals
        self.output_signals_page = OutputSignalsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.output_signals_page)

        self.encoders_page = EncodersMPGsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.encoders_page)  # Index 4

        self.motor_profiles_page = MotorProfilesWidget(self.config_manager)
        self.stacked_widget.addWidget(self.motor_profiles_page)  # Index 5

        self.homing_limits_page = HomingLimitsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.homing_limits_page)  # Index 6

        self.slave_axis_page = SlaveAxisWidget(self.config_manager)
        self.stacked_widget.addWidget(self.slave_axis_page)  # Index 7

        self.backlash_page = BacklashCompWidget(self.config_manager)
        self.stacked_widget.addWidget(self.backlash_page)  # Index 8

        self.eth_mc_adv_page = EthMcAdvancedWidget(self.config_manager)
        self.stacked_widget.addWidget(self.eth_mc_adv_page)  # Index 9

        self.motion_planner_page = MotionPlannerWidget(self.config_manager)
        self.stacked_widget.addWidget(self.motion_planner_page)  # Index 10

        self.spindle_coolant_page = SpindleCoolantWidget(self.config_manager)
        self.stacked_widget.addWidget(self.spindle_coolant_page)  # Index 11

        self.general_thc_page = GeneralThcWidget(self.config_manager)
        self.stacked_widget.addWidget(self.general_thc_page)  # Index 12

        self.internal_thc_page = InternalThcWidget(self.config_manager)
        self.stacked_widget.addWidget(self.internal_thc_page)  # Index 13

        self.button_scripts_page = ButtonScriptsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.button_scripts_page) # Index 14

        self.external_buttons_page = ExternalButtonsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.external_buttons_page) # Index 15

        self.persist_options_page = PersistOptionsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.persist_options_page) # Index 16

        self.ui_options_page = UiOptionsWidget(self.config_manager)
        self.stacked_widget.addWidget(self.ui_options_page) # Index 17

        # Index 18: Placeholder për faqet e tjera në proces zhvillimi
        self.placeholder_page = QWidget()
        ph_layout = QVBoxLayout(self.placeholder_page)
        self.lbl_placeholder = QLabel(
            "Konfigurimi për këtë seksion do të shtohet së shpejti."
        )
        self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(self.lbl_placeholder)
        self.stacked_widget.addWidget(self.placeholder_page)

        content_layout.addWidget(self.stacked_widget, stretch=1)
        root_layout.addLayout(content_layout)

        # Butonat në fund të dritares
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

        self.tree.currentItemChanged.connect(self.on_tree_selection_changed)
        self.tree.setCurrentItem(item_gen)

    def on_tree_selection_changed(self, current, previous):
        if not current:
            return

        if current.childCount() > 0:
            current.setExpanded(True)
            first_child = current.child(0)
            self.tree.setCurrentItem(first_child)
            return

        text = current.text(0)
        if text == "General settings":
            self.stacked_widget.setCurrentIndex(0)
        elif text == "Axis output pins":
            self.stacked_widget.setCurrentIndex(1)
        elif text == "Input signals":
            self.stacked_widget.setCurrentIndex(2)
        elif text == "Output signals":
            self.stacked_widget.setCurrentIndex(3)
        elif text == "Encoders & MPGs":
            self.stacked_widget.setCurrentIndex(4)
        elif text == "Motor profiles":
            self.stacked_widget.setCurrentIndex(5)
        elif text == "Homing/Limits":
            self.stacked_widget.setCurrentIndex(6)
        elif text == "Slave axis":
            self.stacked_widget.setCurrentIndex(7)
        elif text == "Backlash compens.":
            self.stacked_widget.setCurrentIndex(8)
        elif text == "ETH-MC Advanced":
            self.stacked_widget.setCurrentIndex(9)
        elif text == "Motion planner":
            self.stacked_widget.setCurrentIndex(10)
        elif text == "Spindle & Coolant":
            self.stacked_widget.setCurrentIndex(11)
        elif text == "General THC":
            self.stacked_widget.setCurrentIndex(12)    
        elif text == "Internal THC":
            self.stacked_widget.setCurrentIndex(13)
        elif text == "Button scripts":
            self.stacked_widget.setCurrentIndex(14)
        elif text == "External buttons":
            self.stacked_widget.setCurrentIndex(15)
        elif text == "Persist options":
            self.stacked_widget.setCurrentIndex(16)
        elif text == "UI options":
            self.stacked_widget.setCurrentIndex(17)
        else:
            self.lbl_placeholder.setText(
                f"Seksioni: [{text}] - Në proces zhvillimi"
            )
            self.stacked_widget.setCurrentIndex(18)

    def accept(self):
        # Ruajtja e cilësimeve nga secila faqe
        self.general_page.save_settings()
        self.axis_pins_page.save_settings()
        self.input_signals_page.save_settings()
        self.output_signals_page.save_settings()
        self.encoders_page.save_settings()
        self.motor_profiles_page.save_settings()
        self.homing_limits_page.save_settings()
        self.slave_axis_page.save_settings()
        self.backlash_page.save_settings()
        self.eth_mc_adv_page.save_settings()
        self.motion_planner_page.save_settings()
        self.spindle_coolant_page.save_settings()
        self.general_thc_page.save_settings()
        self.internal_thc_page.save_settings()
        self.button_scripts_page.save_settings()
        self.external_buttons_page.save_settings()
        self.persist_options_page.save_settings()
        self.ui_options_page.save_settings()

        if self.config_manager and hasattr(self.config_manager, "save_config"):
            self.config_manager.save_config()

        super().accept()