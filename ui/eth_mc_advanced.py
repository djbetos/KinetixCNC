from typing import Optional, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class EthMcAdvancedWidget(QWidget):
    """Faqja Eth-mc advanced - çaktivizohet automatikisht nëse nuk përdoret kontrollues ETH-MC."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.axes_list = ["X", "Y", "Z", "A", "B", "C", "Spindle"]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Axis",
            "Output type",
            "Max frequency [kHz]",
            "Pulse width [ns]",
        ])

        self.table.setRowCount(len(self.axes_list))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 80)

        main_layout.addWidget(self.table)

        note_label = QLabel(
            "NOTE: Pulse widths are rounded to 20nS resolution. Specify 0 for 50% duty cycle"
        )
        note_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #A0A0A0; margin-top: 15px;"
        )
        note_label.setWordWrap(True)
        main_layout.addWidget(note_label)

        main_layout.addStretch()

    def load_data(self):
        output_types = ["Step/Dir", "CW/CCW", "Quadrature"]

        # Verifikimi i llojit të kontrolluesit (ETH-MC ose ETH-MCI)
        controller_type = "DEMO"
        if self.config_manager:
            controller_type = self.config_manager.get(
                "MotionController", "ControllerType", fallback="DEMO"
            ).upper()

        # Tabela lejohet të modifikohet vetëm nëse është kontrollues ETH
        is_eth_controller = "ETH" in controller_type

        for row, ax in enumerate(self.axes_list):
            out_type = "Step/Dir"
            max_freq = 5000
            pulse_width = 0

            if self.config_manager:
                sec = f"ETH_MC_{ax}"
                out_type = self.config_manager.get(sec, "OutputType", fallback="Step/Dir")
                max_freq = int(self.config_manager.get(sec, "MaxFreqKHz", fallback="5000"))
                pulse_width = int(self.config_manager.get(sec, "PulseWidthNS", fallback="0"))

            item_axis = QTableWidgetItem(ax)
            item_axis.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_axis.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_axis)

            combo_type = QComboBox()
            combo_type.addItems(output_types)
            idx = combo_type.findText(out_type)
            if idx != -1:
                combo_type.setCurrentIndex(idx)
            combo_type.setEnabled(is_eth_controller)
            self.table.setCellWidget(row, 1, combo_type)

            spin_freq = QSpinBox()
            spin_freq.setRange(10, 100000)
            spin_freq.setValue(max_freq)
            spin_freq.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin_freq.setEnabled(is_eth_controller)
            self.table.setCellWidget(row, 2, spin_freq)

            spin_pw = QSpinBox()
            spin_pw.setRange(0, 100000)
            spin_pw.setSingleStep(20)
            spin_pw.setValue(pulse_width)
            spin_pw.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin_pw.setEnabled(is_eth_controller)
            self.table.setCellWidget(row, 3, spin_pw)

        # Nëse nuk është kontrollues ETH, e çaktivizojmë të gjithë tabelën vizualisht
        self.table.setEnabled(is_eth_controller)

    def save_settings(self):
        if not self.config_manager or not self.table.isEnabled():
            return

        for row, ax in enumerate(self.axes_list):
            sec = f"ETH_MC_{ax}"

            combo_type = cast(Optional[QComboBox], self.table.cellWidget(row, 1))
            spin_freq = cast(Optional[QSpinBox], self.table.cellWidget(row, 2))
            spin_pw = cast(Optional[QSpinBox], self.table.cellWidget(row, 3))

            out_type = combo_type.currentText() if combo_type is not None else "Step/Dir"
            max_freq = spin_freq.value() if spin_freq is not None else 5000
            pulse_width = spin_pw.value() if spin_pw is not None else 0

            self.config_manager.set(sec, "OutputType", out_type)
            self.config_manager.set(sec, "MaxFreqKHz", str(max_freq))
            self.config_manager.set(sec, "PulseWidthNS", str(pulse_width))