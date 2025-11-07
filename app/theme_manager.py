import json, os, tkinter as tk
from tkinter import ttk

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".json_formatter_config.json")


class ThemeManager:
    def __init__(self, root: tk.Tk, text_widgets=(), treeview=None):
        self.root = root
        self.text_widgets = list(text_widgets)
        self.treeview = treeview
        self.style = ttk.Style()
        self.theme = None

    # Public
    def load_theme(self, theme_dict: dict):
        self.theme = theme_dict
        self._apply_root()
        self._apply_style()
        self._apply_texts()
        self._apply_treeview()

    def add_text_widget(self, w: tk.Text):
        self.text_widgets.append(w)
        self._style_text_widget(w)

    def set_highlight_tag(self, tag_name="search_match"):
        # Apply Highlight for chosen theme
        for w in self.text_widgets:
            if not w:
                continue
            w.tag_configure(
                tag_name, background=self.theme["hl_bg"], foreground=self.theme["hl_fg"]
            )

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
    def _apply_root(self):
        self.root.configure(bg=self.theme["bg"])

    def _apply_style(self):
        # Global style options
        self.style.configure(
            ".", background=self.theme["bg"], foreground=self.theme["fg"]
        )

        # Button - Enhanced styling for better color visibility
        self.style.configure(
            "TButton",
            background=self.theme["btn_bg"],
            foreground=self.theme["btn_fg"],
            padding=6,
            borderwidth=1,
            relief="raised",
        )
        self.style.map(
            "TButton",
            background=[
                ("active", self._shade(self.theme["btn_bg"], 15)),
                ("pressed", self._shade(self.theme["btn_bg"], -10)),
                ("disabled", self._shade(self.theme["btn_bg"], -20)),
            ],
            foreground=[
                ("active", self.theme["btn_fg"]),
                ("pressed", self.theme["btn_fg"]),
                ("disabled", self._shade(self.theme["btn_fg"], -30)),
            ],
            relief=[("pressed", "sunken")],
        )

        # Label, Frame
        self.style.configure(
            "TLabel", background=self.theme["bg"], foreground=self.theme["fg"]
        )
        self.style.configure("TFrame", background=self.theme["bg"])

        # Entry
        self.style.configure(
            "TEntry",
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["entry_fg"],
        )

        # Notebook
        self.style.configure("TNotebook", background=self.theme["bg"])
        self.style.configure(
            "TNotebook.Tab",
            background=self.theme["btn_bg"],
            foreground=self.theme["btn_fg"],
            padding=[8, 4],
        )

        # Treeview
        self.style.configure(
            "Treeview",
            background=self.theme["tv_bg"],
            foreground=self.theme["tv_fg"],
            fieldbackground=self.theme["tv_bg"],
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.theme["tv_sel_bg"])],
            foreground=[("selected", self.theme["tv_sel_fg"])],
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.theme["tv_header_bg"],
            foreground=self.theme["tv_header_fg"],
        )

    def _apply_texts(self):
        for w in self.text_widgets:
            self._style_text_widget(w)

    def _style_text_widget(self, w: tk.Text):
        w.configure(
            bg=self.theme["text_bg"],
            fg=self.theme["text_fg"],
            insertbackground=self.theme["fg"],  # caret
            selectbackground=self.theme["text_sel_bg"],
            selectforeground=self.theme["text_sel_fg"],
        )

    def _apply_treeview(self):
        if not self.treeview:
            return
        # ttk.Style đã set, đảm bảo rowheight nếu cần
        try:
            self.style.configure("Treeview", rowheight=22)
        except Exception:
            pass

    # helper: chỉnh độ sáng màu hex
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
