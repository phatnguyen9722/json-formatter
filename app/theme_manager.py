import json, os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QTreeWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".json_formatter_config.json")


class ThemeManager:
    def __init__(self, root: QMainWindow, text_widgets=(), treeview=None):
        self.root = root
        self.text_widgets = list(text_widgets)
        self.treeview = treeview
        self.theme = None
        self.app = QApplication.instance()

    # Public
    def load_theme(self, theme_dict: dict):
        self.theme = theme_dict
        self._apply_palette()
        self._apply_stylesheet()
        self._apply_texts()
        self._apply_treeview()

    def add_text_widget(self, w: QTextEdit):
        self.text_widgets.append(w)
        self._style_text_widget(w)

    def set_highlight_tag(self, tag_name="search_match"):
        # Apply Highlight for chosen theme
        for w in self.text_widgets:
            if not w:
                continue
            # Store highlight colors for use in search utilities
            w._highlight_bg = self.theme["hl_bg"]
            w._highlight_fg = self.theme["hl_fg"]

    def save_choice(self):
        if not self.theme:
            return
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"theme": self.theme["name"]}, f)
        except Exception:
            pass

    @staticmethod
    def load_choice_name(default="light"):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("theme", default)
        except Exception:
            pass
        return default

    # Internal apply
    def _apply_palette(self):
        """Apply color palette to the application."""
        if not self.app:
            return

        palette = self.app.palette()

        # Convert hex colors to QColor
        def hex_to_color(hex_color):
            return QColor(hex_color)

        # Set window colors
        palette.setColor(QPalette.Window, hex_to_color(self.theme["bg"]))
        palette.setColor(QPalette.WindowText, hex_to_color(self.theme["fg"]))

        # Set base colors for text widgets
        palette.setColor(QPalette.Base, hex_to_color(self.theme["text_bg"]))
        palette.setColor(QPalette.Text, hex_to_color(self.theme["text_fg"]))

        # Set button colors
        palette.setColor(QPalette.Button, hex_to_color(self.theme["btn_bg"]))
        palette.setColor(QPalette.ButtonText, hex_to_color(self.theme["btn_fg"]))

        # Set highlight colors
        palette.setColor(QPalette.Highlight, hex_to_color(self.theme["text_sel_bg"]))
        palette.setColor(
            QPalette.HighlightedText, hex_to_color(self.theme["text_sel_fg"])
        )

        self.app.setPalette(palette)

    def _apply_stylesheet(self):
        """Apply Qt stylesheet for enhanced styling."""
        if not self.app:
            return

        stylesheet = f"""
        QMainWindow {{
            background-color: {self.theme["bg"]};
            color: {self.theme["fg"]};
        }}
        
        QWidget {{
            background-color: {self.theme["bg"]};
            color: {self.theme["fg"]};
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }}
        
        QPushButton {{
            background-color: {self.theme["btn_bg"]};
            color: {self.theme["btn_fg"]};
            border: 1px solid {self._shade(self.theme["btn_bg"], -20)};
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {self._shade(self.theme["btn_bg"], 15)};
        }}
        
        QPushButton:pressed {{
            background-color: {self._shade(self.theme["btn_bg"], -10)};
        }}
        
        QLabel {{
            background-color: {self.theme["bg"]};
            color: {self.theme["fg"]};
        }}
        
        QLineEdit {{
            background-color: {self.theme["entry_bg"]};
            color: {self.theme["entry_fg"]};
            border: 1px solid {self._shade(self.theme["entry_bg"], -30)};
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {self._shade(self.theme["bg"], -20)};
            background-color: {self.theme["bg"]};
        }}
        
        QTabBar::tab {{
            background-color: {self.theme["btn_bg"]};
            color: {self.theme["btn_fg"]};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.theme["bg"]};
            border-bottom: 2px solid {self.theme["btn_bg"]};
        }}
        
        QTreeWidget {{
            background-color: {self.theme["tv_bg"]};
            color: {self.theme["tv_fg"]};
            alternate-background-color: {self._shade(self.theme["tv_bg"], 5)};
            border: 1px solid {self._shade(self.theme["tv_bg"], -20)};
        }}
        
        QTreeWidget::item:selected {{
            background-color: {self.theme["tv_sel_bg"]};
            color: {self.theme["tv_sel_fg"]};
        }}
        
        QTreeWidget::header {{
            background-color: {self.theme["tv_header_bg"]};
            color: {self.theme["tv_header_fg"]};
            border: 1px solid {self._shade(self.theme["tv_header_bg"], -20)};
            padding: 4px;
            font-weight: bold;
        }}
        
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: url(none);
        }}
        
        QTextEdit {{
            background-color: {self.theme["text_bg"]};
            color: {self.theme["text_fg"]};
            border: 1px solid {self._shade(self.theme["text_bg"], -20)};
            selection-background-color: {self.theme["text_sel_bg"]};
            selection-color: {self.theme["text_sel_fg"]};
        }}
        
        QRadioButton, QCheckBox {{
            background-color: {self.theme["bg"]};
            color: {self.theme["fg"]};
            spacing: 8px;
        }}
        
        QRadioButton::indicator, QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        """

        self.app.setStyleSheet(stylesheet)

    def _apply_texts(self):
        for w in self.text_widgets:
            self._style_text_widget(w)

    def _style_text_widget(self, w: QTextEdit):
        """Apply styling to a text widget."""
        # Store theme colors for use in search utilities
        w._theme_bg = self.theme["text_bg"]
        w._theme_fg = self.theme["text_fg"]
        w._theme_sel_bg = self.theme["text_sel_bg"]
        w._theme_sel_fg = self.theme["text_sel_fg"]

        # Set font for better readability
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.TypeWriter)
        w.setFont(font)

    def _apply_treeview(self):
        if not self.treeview:
            return
        # Set font for tree widget
        font = QFont("Segoe UI", 9)
        self.treeview.setFont(font)

        # Store theme colors for use in tree utilities
        self.treeview._theme_bg = self.theme["tv_bg"]
        self.treeview._theme_fg = self.theme["tv_fg"]
        self.treeview._theme_sel_bg = self.theme["tv_sel_bg"]
        self.treeview._theme_sel_fg = self.theme["tv_sel_fg"]

    # helper: Modify hex color
    def _shade(self, hex_color, percent=-10):
        # percent: -100..+100
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return "#" + hex_color
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        def clamp(x):
            return max(0, min(255, x))

        r = clamp(int(r * (100 + percent) / 100))
        g = clamp(int(g * (100 + percent) / 100))
        b = clamp(int(b * (100 + percent) / 100))
        return f"#{r:02X}{g:02X}{b:02X}"
