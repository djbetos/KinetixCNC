from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class IoDiagnosticsDialog(QDialog):
    """Dritarja e diagnostikimit IO (Modeless), e cila lejon përdorimin e pjesëve të tjera të aplikacionit njëkohësisht."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("ETH-MCI IO diagnostics...")
        self.resize(340, 520)

        # Sigurohemi që dritarja të jetë e pavarur dhe të mos bllokojë dritaren kryesore
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Input pins (1 - 24)
        group_in_pins = QGroupBox("Input pins")
        v_in_pins = QVBoxLayout(group_in_pins)
        
        # Rreshti i parë (1-12)
        grid_in1 = QGridLayout()
        grid_in1.setSpacing(4)
        for i in range(1, 13):
            lbl_num = QLabel(str(i))
            lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_num.setStyleSheet("color: #CCCCCC; font-size: 10px;")
            grid_in1.addWidget(lbl_num, 0, i - 1)

            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet("color: #555555; font-size: 14px;")  # Gri = Off, Jeshile/Kuqe kur është aktiv
            grid_in1.addWidget(dot, 1, i - 1)
        v_in_pins.addLayout(grid_in1)

        # Rreshti i dytë (13-24)
        grid_in2 = QGridLayout()
        grid_in2.setSpacing(4)
        for i in range(13, 25):
            lbl_num = QLabel(str(i))
            lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_num.setStyleSheet("color: #CCCCCC; font-size: 10px;")
            grid_in2.addWidget(lbl_num, 0, i - 13)

            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet("color: #555555; font-size: 14px;")
            grid_in2.addWidget(dot, 1, i - 13)
        v_in_pins.addLayout(grid_in2)

        main_layout.addWidget(group_in_pins)

        # 2. Output pins (1 - 24)
        group_out_pins = QGroupBox("Output pins")
        v_out_pins = QVBoxLayout(group_out_pins)

        grid_out1 = QGridLayout()
        grid_out1.setSpacing(4)
        for i in range(1, 13):
            lbl_num = QLabel(str(i))
            lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_num.setStyleSheet("color: #CCCCCC; font-size: 10px;")
            grid_out1.addWidget(lbl_num, 0, i - 1)

            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet("color: #555555; font-size: 14px;")
            grid_out1.addWidget(dot, 1, i - 1)
        v_out_pins.addLayout(grid_out1)

        grid_out2 = QGridLayout()
        grid_out2.setSpacing(4)
        for i in range(13, 25):
            lbl_num = QLabel(str(i))
            lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_num.setStyleSheet("color: #CCCCCC; font-size: 10px;")
            grid_out2.addWidget(lbl_num, 0, i - 13)

            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet("color: #555555; font-size: 14px;")
            grid_out2.addWidget(dot, 1, i - 13)
        v_out_pins.addLayout(grid_out2)

        main_layout.addWidget(group_out_pins)

        # Butoni zvogëlues/zgjerues sipas fotos
        h_btn_collapse = QHBoxLayout()
        h_btn_collapse.addStretch()
        btn_collapse = QPushButton("<<")
        btn_collapse.setFixedWidth(50)
        h_btn_collapse.addWidget(btn_collapse)
        main_layout.addLayout(h_btn_collapse)

        # 3. Input signals (Limit-, Limit+, Home, etj.)
        group_in_signals = QGroupBox("Input signals")
        grid_sig = QGridLayout(group_in_signals)
        grid_sig.setSpacing(6)

        axes = ["X", "Y", "Z", "A", "B", "C"]
        for col, ax in enumerate(axes, start=1):
            lbl_ax = QLabel(ax)
            lbl_ax.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_sig.addWidget(lbl_ax, 0, col)

        signals = ["Limit-", "Limit+", "Home"]
        for row, sig in enumerate(signals, start=1):
            lbl_sig = QLabel(sig)
            grid_sig.addWidget(lbl_sig, row, 0)
            for col in range(1, 7):
                dot = QLabel("●")
                dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dot.setStyleSheet("color: #555555; font-size: 14px;")
                grid_sig.addWidget(dot, row, col)

        # Sinjalet e poshtme (Probe, Index, EStop)
        h_bot_sigs = QHBoxLayout()
        h_bot_sigs.addWidget(QRadioButton("Probe"))
        h_bot_sigs.addWidget(QRadioButton("Index"))
        h_bot_sigs.addWidget(QRadioButton("EStop"))
        
        v_sig_layout = QVBoxLayout(group_in_signals)
        v_sig_layout.addLayout(grid_sig)
        v_sig_layout.addLayout(h_bot_sigs)

        main_layout.addWidget(group_in_signals)
        main_layout.addStretch()