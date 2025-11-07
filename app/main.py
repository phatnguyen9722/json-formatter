import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from .controller import Controller
from .tree_utils import insert_to_tree
from .search_utils import (
    setup_highlight,
    clear_highlight,
    highlight_all,
    find_next,
    find_prev,
)
from .theme_manager import ThemeManager
from .themes.light import THEME as LIGHT
from .themes.dark import THEME as DARK
from .themes.wine_red import THEME as WINE_RED


class AppUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("JSON/Python Formatter (Modular)")
        self.controller = Controller(self)
        self._build_widgets()
        self.theme_manager = ThemeManager(
            root=self.root,
            text_widgets=(self.input_box, self.output_box),
            treeview=self.tree,
        )

        # load theme
        chosen = ThemeManager.load_choice_name("light")
        self._apply_theme(chosen)

        # menu switch theme
        self._build_menu()

        # search highlight dùng theme
        self.theme_manager.set_highlight_tag("search_match")

    # --- UI build ---
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(
            label="Light", command=lambda: self._apply_theme("light")
        )
        theme_menu.add_command(label="Dark", command=lambda: self._apply_theme("dark"))
        theme_menu.add_command(
            label="Wine Red", command=lambda: self._apply_theme("wine_red")
        )
        menubar.add_cascade(label="Theme", menu=theme_menu)
        self.root.config(menu=menubar)

    def _apply_theme(self, name: str):
        if name == "dark":
            self.theme_manager.load_theme(DARK)
        elif name == "wine_red":
            self.theme_manager.load_theme(WINE_RED)
        else:
            self.theme_manager.load_theme(LIGHT)
        self.theme_manager.set_highlight_tag("search_match")
        self.theme_manager.save_choice()

    def _build_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.frame_input = ttk.Frame(self.notebook)
        self.frame_json = ttk.Frame(self.notebook)
        self.frame_tree = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_input, text="Input")
        self.notebook.add(self.frame_json, text="Pretty JSON")
        self.notebook.add(self.frame_tree, text="Tree")
        self.notebook.pack(fill="both", expand=True)

        # Input / Output
        self.input_box = ScrolledText(self.frame_input, height=18, undo=True)
        self.input_box.pack(fill="both", expand=True, padx=8, pady=8)

        self.output_box = ScrolledText(self.frame_json, height=18, undo=True)
        self.output_box.pack(fill="both", expand=True, padx=8, pady=8)

        # Tree
        self.tree = ttk.Treeview(
            self.frame_tree, columns=("type", "value"), show="tree headings"
        )
        self.tree.heading("#0", text="Key / Index")
        self.tree.heading("type", text="Type")
        self.tree.heading("value", text="Value")
        self.tree.column("#0", stretch=True, width=320)
        self.tree.column("type", width=120, anchor="w")
        self.tree.column("value", stretch=True, width=400)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Buttons
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Button(
            bar, text="Convert → Pretty", command=self.controller.convert_pretty
        ).pack(side="left", padx=4)
        ttk.Button(bar, text="Build Tree", command=self.controller.build_tree).pack(
            side="left", padx=4
        )
        ttk.Button(bar, text="Minify JSON", command=self.controller.minify).pack(
            side="left", padx=4
        )
        ttk.Button(
            bar, text="Generate TypedDict", command=self.controller.generate_typeddict
        ).pack(side="left", padx=4)
        ttk.Button(bar, text="Clear Input", command=self.clear_input).pack(
            side="right", padx=4
        )
        ttk.Button(bar, text="Clear Output", command=self.clear_output).pack(
            side="right", padx=4
        )

        # Search bar
        sbar = ttk.Frame(self.root)
        sbar.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(sbar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(sbar, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=4)

        self.target_var = tk.StringVar(value="input")
        ttk.Radiobutton(
            sbar, text="Input", variable=self.target_var, value="input"
        ).pack(side="left", padx=(8, 2))
        ttk.Radiobutton(
            sbar, text="Output", variable=self.target_var, value="output"
        ).pack(side="left", padx=2)

        self.case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sbar, text="Case-sensitive", variable=self.case_var).pack(
            side="left", padx=8
        )

        ttk.Button(sbar, text="Highlight All", command=self.on_highlight_all).pack(
            side="left", padx=4
        )
        ttk.Button(sbar, text="Find Next (F3)", command=self.on_find_next).pack(
            side="left", padx=4
        )
        ttk.Button(sbar, text="Find Prev (Shift+F3)", command=self.on_find_prev).pack(
            side="left", padx=4
        )
        ttk.Button(sbar, text="Clear Highlight", command=self.on_clear_highlight).pack(
            side="left", padx=4
        )

        # Highlight config
        setup_highlight(self.input_box)
        setup_highlight(self.output_box)

        # Shortcuts
        self.root.bind(
            "<Control-f>", lambda e: (self.search_entry.focus_set(), "break")
        )
        self.root.bind("<F3>", lambda e: (self.on_find_next(), "break"))
        self.root.bind("<Shift-F3>", lambda e: (self.on_find_prev(), "break"))

        # Ctrl-A to query all data in notebook
        for box in (self.input_box, self.output_box):
            box.bind("<Control-a>", self.select_all)
            box.bind("<Control-A>", self.select_all)

    # --- UI ↔ Controller helpers ---
    def get_input(self) -> str:
        return self.input_box.get("1.0", tk.END)

    def select_all(self, event=None):
        widget = event.widget
        widget.tag_add("sel", "1.0", "end-1c")
        return "break"

    def set_output(self, text: str):
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)

    def load_tree(self, data):
        # clear
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            if isinstance(data, dict):
                root_id = self.tree.insert(
                    "", "end", text="root(dict)", values=("dict", "")
                )
                for k, v in data.items():
                    insert_to_tree(self.tree, root_id, k, v)
                self.tree.item(root_id, open=True)
            elif isinstance(data, list):
                root_id = self.tree.insert(
                    "", "end", text=f"root(list[{len(data)}])", values=("list", "")
                )
                for i, v in enumerate(data):
                    insert_to_tree(self.tree, root_id, f"[{i}]", v)
                self.tree.item(root_id, open=True)
            else:
                self.tree.insert(
                    "",
                    "end",
                    text="root(value)",
                    values=(type(data).__name__, str(data)),
                )
        except Exception as e:
            messagebox.showerror("Tree error", str(e))

    def show_tab_json(self):
        self.notebook.select(self.frame_json)

    def show_tab_tree(self):
        self.notebook.select(self.frame_tree)

    # --- Clear ---
    def clear_input(self):
        self.input_box.delete("1.0", tk.END)

    def clear_output(self):
        self.output_box.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)

    # --- Search ops ---
    def _target_text(self):
        return self.input_box if self.target_var.get() == "input" else self.output_box

    def on_highlight_all(self):
        txt = self._target_text()
        highlight_all(txt, self.search_var.get(), self.case_var.get())

    def on_find_next(self):
        txt = self._target_text()
        # highlight handle
        if not txt.tag_ranges("search_match"):
            highlight_all(txt, self.search_var.get(), self.case_var.get())
        else:
            find_next(txt, self.search_var.get(), self.case_var.get())

    def on_find_prev(self):
        txt = self._target_text()
        if not txt.tag_ranges("search_match"):
            highlight_all(txt, self.search_var.get(), self.case_var.get())
        else:
            find_prev(txt, self.search_var.get(), self.case_var.get())

    def on_clear_highlight(self):
        clear_highlight(self._target_text())


def main():
    root = tk.Tk()
    AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
