from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFontDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class UiOptionsWidget(QWidget):
    """Faqja UI options për personalizimin e interfaqes, fontit dhe ngjyrave të G-code."""

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.elements_list = [
            ("Background color", "#FFFFFF"),
            ("Selected background", "#CCCCFF"),
            ("N, line number", "#8B0000"),
            ("G command", "#0000FF"),
            ("X-A axis coordinates", "#000000"),
            ("I, J, K parameters", "#008000"),
            ("M macro", "#00008B"),
            ("F, S command", "#B8860B"),
            ("O, subroutine", "#800080"),
            ("Comment", "#808080"),
            ("P, Q, R... parameters", "#00BFFF"),
        ]

        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Rreshti i Sipërm: Window scale factor & Macro log window
        top_h = QHBoxLayout()
        top_h.setSpacing(25)

        # Window scale & Font button
        v_scale = QVBoxLayout()
        h_scale = QHBoxLayout()
        lbl_scale = QLabel("Window scale factor")
        self.txt_scale = QLineEdit("1.1")
        self.txt_scale.setFixedWidth(70)
        h_scale.addWidget(lbl_scale)
        h_scale.addWidget(self.txt_scale)
        
        self.btn_font = QPushButton("G-Code font...")
        self.btn_font.setFixedWidth(110)
        self.btn_font.clicked.connect(self.on_choose_font)

        v_scale.addLayout(h_scale)
        v_scale.addWidget(self.btn_font)
        v_scale.addStretch()
        top_h.addLayout(v_scale)

        # Macro log window Group
        group_macro = QGroupBox("Macro log window")
        v_macro = QVBoxLayout(group_macro)
        self.chk_auto_err = QCheckBox("Auto open on script error")
        self.chk_auto_msg = QCheckBox("Auto open on any message")
        v_macro.addWidget(self.chk_auto_err)
        v_macro.addWidget(self.chk_auto_msg)
        top_h.addWidget(group_macro)

        top_h.addStretch()
        main_layout.addLayout(top_h)

        # Checkboxes për Syntax Highlighting dhe Tooltips
        mid_opts_h = QHBoxLayout()
        self.chk_syntax = QCheckBox("Syntax highlighting")
        self.chk_syntax.setChecked(True)
        self.chk_tooltips = QCheckBox("Show tooltips")
        self.chk_tooltips.setChecked(True)

        mid_opts_h.addWidget(self.chk_syntax)
        mid_opts_h.addSpacing(40)
        mid_opts_h.addWidget(self.chk_tooltips)
        mid_opts_h.addStretch()
        main_layout.addLayout(mid_opts_h)

        self.chk_custom_colors = QCheckBox("Customize colors for G-Code view")
        self.chk_custom_colors.toggled.connect(self.toggle_color_customization)
        main_layout.addWidget(self.chk_custom_colors)

        # Pjesa e Poshtme: Tabela e Ngjyrave dhe Butonat Default (Light/Dark)
        table_row_h = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Element", "Color"])
        self.table.setRowCount(len(self.elements_list))
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        table_row_h.addWidget(self.table)

        # Butonat Default (light / dark) në të djathtë të tabelës
        v_def_btns = QVBoxLayout()
        v_def_btns.setSpacing(10)
        
        self.btn_light = QPushButton("Default colors\n(light)")
        self.btn_light.setFixedWidth(110)
        self.btn_light.setFixedHeight(50)
        self.btn_light.clicked.connect(self.set_default_light)

        self.btn_dark = QPushButton("Default colors\n(dark)")
        self.btn_dark.setFixedWidth(110)
        self.btn_dark.setFixedHeight(50)
        self.btn_dark.clicked.connect(self.set_default_dark)

        v_def_btns.addWidget(self.btn_light)
        v_def_btns.addWidget(self.btn_dark)
        v_def_btns.addStretch()

        table_row_h.addLayout(v_def_btns)
        main_layout.addLayout(table_row_h)

        # Lidhni ngjarjen e klikimit në qeliza të tabelës për ndryshimin e ngjyrës
        self.table.cellClicked.connect(self.on_cell_clicked)

    def toggle_color_customization(self, enabled: bool):
        self.table.setEnabled(enabled)
        self.btn_light.setEnabled(enabled)
        self.btn_dark.setEnabled(enabled)

    def on_choose_font(self):
        ok, font = QFontDialog.getFont(self)
        if ok:
            self.selected_font = font

    def on_cell_clicked(self, row: int, col: int):
        if col == 1:
            item = self.table.item(row, col)
            if item is not None:
                current_color = item.background().color()
                color = QColorDialog.getColor(current_color, self, "Zgjidh ngjyrën")
                if color.isValid():
                    item.setBackground(color)

    def set_default_light(self):
        light_colors = ["#FFFFFF", "#CCCCFF", "#8B0000", "#0000FF", "#000000", "#008000", "#00008B", "#B8860B", "#800080", "#808080", "#00BFFF"]
        for row, (_, default_hex) in enumerate(self.elements_list):
            hex_c = light_colors[row] if row < len(light_colors) else default_hex
            item = self.table.item(row, 1)
            if item is not None:
                item.setBackground(QColor(hex_c))

    def set_default_dark(self):
        dark_colors = ["#1E1E1E", "#3A3D41", "#F14C4C", "#3794FF", "#D4D4D4", "#4EC9B0", "#569CD6", "#CE9178", "#C586C0", "#6A9955", "#4FC1FF"]
        for row, (_, default_hex) in enumerate(self.elements_list):
            hex_c = dark_colors[row] if row < len(dark_colors) else default_hex
            item = self.table.item(row, 1)
            if item is not None:
                item.setBackground(QColor(hex_c))

    def load_data(self):
        scale = "1.1"
        auto_err = False
        auto_msg = False
        syntax = True
        tooltips = True
        custom_col = False

        if self.config_manager:
            scale = self.config_manager.get("UI", "ScaleFactor", "1.1")
            auto_err = self.config_manager.get_boolean("UI", "MacroErrorAutoOpen", False)
            auto_msg = self.config_manager.get_boolean("UI", "MacroMsgAutoOpen", False)
            syntax = self.config_manager.get_boolean("UI", "SyntaxHighlight", True)
            tooltips = self.config_manager.get_boolean("UI", "ShowTooltips", True)
            custom_col = self.config_manager.get_boolean("UI", "CustomColorsEnable", False)

        self.txt_scale.setText(scale)
        self.chk_auto_err.setChecked(auto_err)
        self.chk_auto_msg.setChecked(auto_msg)
        self.chk_syntax.setChecked(syntax)
        self.chk_tooltips.setChecked(tooltips)
        self.chk_custom_colors.setChecked(custom_col)
        self.toggle_color_customization(custom_col)

        for row, (elem_name, default_hex) in enumerate(self.elements_list):
            item_name = QTableWidgetItem(elem_name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_name)

            color_hex = default_hex
            if self.config_manager:
                color_hex = self.config_manager.get("UI_COLORS", elem_name.replace(' ', '_').replace(',', ''), default_hex)

            item_color = QTableWidgetItem()
            item_color.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_color.setBackground(QColor(color_hex))
            self.table.setItem(row, 1, item_color)

    def save_settings(self):
        if not self.config_manager:
            return

        self.config_manager.set("UI", "ScaleFactor", self.txt_scale.text())
        self.config_manager.set("UI", "MacroErrorAutoOpen", str(self.chk_auto_err.isChecked()))
        self.config_manager.set("UI", "MacroMsgAutoOpen", str(self.chk_auto_msg.isChecked()))
        self.config_manager.set("UI", "SyntaxHighlight", str(self.chk_syntax.isChecked()))
        self.config_manager.set("UI", "ShowTooltips", str(self.chk_tooltips.isChecked()))
        self.config_manager.set("UI", "CustomColorsEnable", str(self.chk_custom_colors.isChecked()))

        for row, (elem_name, _) in enumerate(self.elements_list):
            item_color = self.table.item(row, 1)
            if item_color is not None:
                bg_color = item_color.background().color().name()
                key = elem_name.replace(' ', '_').replace(',', '')
                self.config_manager.set("UI_COLORS", key, bg_color)