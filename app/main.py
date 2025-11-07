import sys
import os
import platform
from PIL import Image

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QRadioButton,
    QCheckBox,
    QFrame,
    QMenuBar,
    QMenu,
    QMessageBox,
    QSplitter,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFont, QKeySequence, QTextCursor, QAction

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


class AppUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON/Python Formatter (Modular)")

        # storage for QPixmap references
        self._icon_pixmap = None
        self._header_pixmap = None

        self._set_app_icon()
        self.controller = Controller(self)
        self._build_widgets()
        self.theme_manager = ThemeManager(
            root=self,
            text_widgets=(self.input_box, self.output_box),
            treeview=self.tree,
        )

        # load theme
        chosen = ThemeManager.load_choice_name("light")
        self._apply_theme(chosen)

        # menu switch theme
        self._build_menu()

        # search highlight tag uses theme
        self.theme_manager.set_highlight_tag("search_match")

    # -------------------------
    # Helper functions
    # -------------------------
    def _resource_dir(self):
        """Return the directory where assets are located, handling frozen bundles."""
        if getattr(sys, "frozen", False):
            # PyInstaller / similar
            return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    def _make_transparent(
        self, image: Image.Image, threshold: int = 200
    ) -> Image.Image:
        """Turn near-white pixels transparent (preserve alpha if present)."""
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        datas = image.getdata()
        new_data = []
        for r, g, b, a in datas:
            if r > threshold and g > threshold and b > threshold:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))
        image.putdata(new_data)
        return image

    def _load_image(
        self, path: str, size: tuple = None, make_transparent=True
    ) -> Image.Image | None:
        """Load an image from path, optionally make white → transparent, and resize.
        Ensures full pixel data is loaded (avoids 'bad argument type' errors on macOS).
        """
        try:
            with Image.open(path) as img:
                # Force full load into memory before closing the file handle
                img = img.copy()
        except Exception as e:
            print(f"Failed to open image {path}: {e}")
            return None

        try:
            # Always ensure RGBA for Tk compatibility
            img = img.convert("RGBA")

            # Optional transparency cleanup
            if make_transparent:
                datas = img.getdata()
                new_data = []
                for r, g, b, a in datas:
                    if r > 200 and g > 200 and b > 200:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append((r, g, b, a))
                img.putdata(new_data)

            # Optional resizing
            if size:
                resample = getattr(Image, "Resampling", None)
                if resample:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(size, Image.ANTIALIAS)

            return img

        except Exception as e:
            print(f"Failed to process image {path}: {e}")
            return None

    # -------------------------
    # Icon handling
    # -------------------------
    def _set_app_icon(self):
        """Set the application window icon with transparency (cross-platform)."""
        import io
        from PIL import Image

        system = platform.system()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_png = os.path.join(script_dir, "assets", "icon.png")
        icon_ico = os.path.join(script_dir, "assets", "icon.ico")

        try:
            if system == "Darwin":
                try:
                    from AppKit import NSApplication, NSImage

                    if os.path.exists(icon_png):
                        app = NSApplication.sharedApplication()
                        img = NSImage.alloc().initWithContentsOfFile_(icon_png)
                        if img:
                            app.setApplicationIconImage_(img)
                            print("✅ macOS Dock icon set with transparency.")
                    return
                except Exception as e:
                    print(f"Could not set macOS Dock icon: {e}")

            # --- Windows / Linux: use transparent PNG for setWindowIcon() ---
            if os.path.exists(icon_png):
                img = Image.open(icon_png).convert("RGBA")

                # Optional cleanup: remove white-ish backgrounds
                datas = img.getdata()
                new_data = []
                for item in datas:
                    if item[0] > 230 and item[1] > 230 and item[2] > 230:
                        new_data.append((255, 255, 255, 0))  # transparent
                    else:
                        new_data.append(item)
                img.putdata(new_data)

                # Resize to appropriate window icon size
                img = img.resize((256, 256), Image.Resampling.LANCZOS)

                # Convert to Qt pixmap
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                icon = QIcon(pixmap)
                self.setWindowIcon(icon)
                self._icon_ref = icon  # prevent GC
                print("Window icon set with transparency ✅")

            elif os.path.exists(icon_ico):
                # Fallback .ico for Windows
                icon = QIcon(icon_ico)
                self.setWindowIcon(icon)
                print("Fallback .ico icon used ✅")

            else:
                print("No icon found — skipping icon setup.")

        except Exception as e:
            print(f"Could not set Qt icon: {e}")

    # --- UI build ---
    def _build_menu(self):
        menubar = self.menuBar()
        theme_menu = menubar.addMenu("Theme")

        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self._apply_theme("light"))
        theme_menu.addAction(light_action)

        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self._apply_theme("dark"))
        theme_menu.addAction(dark_action)

        wine_red_action = QAction("Wine Red", self)
        wine_red_action.triggered.connect(lambda: self._apply_theme("wine_red"))
        theme_menu.addAction(wine_red_action)

    def _apply_theme(self, name: str):
        if name == "dark":
            self.theme_manager.load_theme(DARK)
        elif name == "wine_red":
            self.theme_manager.load_theme(WINE_RED)
        else:
            self.theme_manager.load_theme(LIGHT)
        self.theme_manager.set_highlight_tag("search_match")
        self.theme_manager.save_choice()

    def _build_header(self):
        """Build the header frame with a safe, delayed icon loader for macOS."""
        from PIL import Image

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 8, 8, 4)

        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "icon.png")

        # Title first (so layout stays stable)
        title_label = QLabel("JSON/Python Formatter")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)

        center_layout.addWidget(title_label)
        header_layout.addWidget(center_widget)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        self.header_widget = header_widget
        self.separator = separator

        def _try_load_icon():
            """Load the header icon after Qt window is realized."""
            if not os.path.exists(icon_path):
                print("Header icon not found.")
                return

            try:
                img = Image.open(icon_path).convert("RGBA")

                # Optional: remove white background
                img_data = []
                for r, g, b, a in img.getdata():
                    if r > 230 and g > 230 and b > 230:
                        img_data.append((255, 255, 255, 0))
                    else:
                        img_data.append((r, g, b, a))
                img.putdata(img_data)

                img = img.resize((32, 32), Image.Resampling.LANCZOS)

                # Convert to Qt pixmap
                import io

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

                icon_label = QLabel()
                icon_label.setPixmap(pixmap)
                icon_label.setFixedSize(32, 32)

                center_layout.insertWidget(0, icon_label)
                center_layout.insertSpacing(1, 8)

            except Exception as e:
                print(f"Could not load header icon: {e}")

        # Wait until window is drawn (macOS-safe)
        QTimer.singleShot(200, _try_load_icon)

    def _build_widgets(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with icon and title
        self._build_header()
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.separator)

        # Tab widget
        self.notebook = QTabWidget()
        self.frame_input = QWidget()
        self.frame_json = QWidget()
        self.frame_tree = QWidget()

        self.notebook.addTab(self.frame_input, "Input")
        self.notebook.addTab(self.frame_json, "Pretty JSON")
        self.notebook.addTab(self.frame_tree, "Tree")
        main_layout.addWidget(self.notebook)

        # Setup tab layouts
        input_layout = QVBoxLayout(self.frame_input)
        input_layout.setContentsMargins(8, 8, 8, 8)

        json_layout = QVBoxLayout(self.frame_json)
        json_layout.setContentsMargins(8, 8, 8, 8)

        tree_layout = QVBoxLayout(self.frame_tree)
        tree_layout.setContentsMargins(8, 8, 8, 8)

        # Input / Output text areas
        self.input_box = QTextEdit()
        self.input_box.setAcceptRichText(False)
        self.input_box.setMinimumHeight(400)
        input_layout.addWidget(self.input_box)

        self.output_box = QTextEdit()
        self.output_box.setAcceptRichText(False)
        self.output_box.setMinimumHeight(400)
        json_layout.addWidget(self.output_box)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key / Index", "Type", "Value"])
        self.tree.setColumnWidth(0, 320)
        self.tree.setColumnWidth(1, 120)
        tree_layout.addWidget(self.tree)

        # Buttons
        bar_widget = QWidget()
        bar_layout = QHBoxLayout(bar_widget)
        bar_layout.setContentsMargins(8, 4, 8, 4)

        convert_btn = QPushButton("Convert → Pretty")
        convert_btn.clicked.connect(self.controller.convert_pretty)
        bar_layout.addWidget(convert_btn)

        tree_btn = QPushButton("Build Tree")
        tree_btn.clicked.connect(self.controller.build_tree)
        bar_layout.addWidget(tree_btn)

        minify_btn = QPushButton("Minify JSON")
        minify_btn.clicked.connect(self.controller.minify)
        bar_layout.addWidget(minify_btn)

        typeddict_btn = QPushButton("Generate TypedDict")
        typeddict_btn.clicked.connect(self.controller.generate_typeddict)
        bar_layout.addWidget(typeddict_btn)

        bar_layout.addStretch()

        clear_output_btn = QPushButton("Clear Output")
        clear_output_btn.clicked.connect(self.clear_output)
        bar_layout.addWidget(clear_output_btn)

        clear_input_btn = QPushButton("Clear Input")
        clear_input_btn.clicked.connect(self.clear_input)
        bar_layout.addWidget(clear_input_btn)

        main_layout.addWidget(bar_widget)

        # Search bar
        sbar_widget = QWidget()
        sbar_layout = QHBoxLayout(sbar_widget)
        sbar_layout.setContentsMargins(8, 0, 8, 8)

        sbar_layout.addWidget(QLabel("Search:"))

        self.search_var = ""
        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self._on_search_text_changed)
        self.search_entry.setMinimumWidth(200)
        sbar_layout.addWidget(self.search_entry)

        self.target_var = "input"
        input_radio = QRadioButton("Input")
        input_radio.setChecked(True)
        input_radio.toggled.connect(
            lambda checked: self._on_target_changed("input") if checked else None
        )
        sbar_layout.addWidget(input_radio)

        output_radio = QRadioButton("Output")
        output_radio.toggled.connect(
            lambda checked: self._on_target_changed("output") if checked else None
        )
        sbar_layout.addWidget(output_radio)

        self.case_var = False
        case_check = QCheckBox("Case-sensitive")
        case_check.toggled.connect(self._on_case_changed)
        sbar_layout.addWidget(case_check)

        highlight_btn = QPushButton("Highlight All")
        highlight_btn.clicked.connect(self.on_highlight_all)
        sbar_layout.addWidget(highlight_btn)

        next_btn = QPushButton("Find Next (F3)")
        next_btn.clicked.connect(self.on_find_next)
        sbar_layout.addWidget(next_btn)

        prev_btn = QPushButton("Find Prev (Shift+F3)")
        prev_btn.clicked.connect(self.on_find_prev)
        sbar_layout.addWidget(prev_btn)

        clear_highlight_btn = QPushButton("Clear Highlight")
        clear_highlight_btn.clicked.connect(self.on_clear_highlight)
        sbar_layout.addWidget(clear_highlight_btn)

        main_layout.addWidget(sbar_widget)

        # Highlight config
        setup_highlight(self.input_box)
        setup_highlight(self.output_box)

        # Shortcuts
        self.shortcut_ctrl_f = QKeySequence("Ctrl+F")
        self.shortcut_f3 = QKeySequence("F3")
        self.shortcut_shift_f3 = QKeySequence("Shift+F3")

        # Connect shortcuts (will be implemented with QAction in main window)
        self._setup_shortcuts()

        # Ctrl-A to select all
        self.input_box.selectAll_shortcut = QKeySequence("Ctrl+A")
        self.output_box.selectAll_shortcut = QKeySequence("Ctrl+A")

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts using QAction."""
        # Ctrl+F - Focus search
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(lambda: self.search_entry.setFocus())
        self.addAction(search_action)

        # F3 - Find next
        f3_action = QAction(self)
        f3_action.setShortcut(QKeySequence("F3"))
        f3_action.triggered.connect(self.on_find_next)
        self.addAction(f3_action)

        # Shift+F3 - Find previous
        shift_f3_action = QAction(self)
        shift_f3_action.setShortcut(QKeySequence("Shift+F3"))
        shift_f3_action.triggered.connect(self.on_find_prev)
        self.addAction(shift_f3_action)

        # Ctrl+A - Select all for text widgets
        select_all_action = QAction(self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self._select_all_in_focused_widget)
        self.addAction(select_all_action)

    def _select_all_in_focused_widget(self):
        """Select all text in the currently focused text widget."""
        focused_widget = self.focusWidget()
        if isinstance(focused_widget, QTextEdit):
            focused_widget.selectAll()

    def _on_search_text_changed(self, text):
        """Handle search text changes."""
        self.search_var = text

    def _on_target_changed(self, target):
        """Handle search target radio button changes."""
        self.target_var = target

    def _on_case_changed(self, checked):
        """Handle case sensitivity checkbox changes."""
        self.case_var = checked

    # --- UI ↔ Controller helpers ---
    def get_input(self) -> str:
        return self.input_box.toPlainText()

    def select_all(self, event=None):
        """Select all text in a widget (for compatibility)."""
        if hasattr(event, "widget") and hasattr(event.widget, "selectAll"):
            event.widget.selectAll()

    def set_output(self, text: str):
        self.output_box.setPlainText(text)

    def load_tree(self, data):
        # clear
        self.tree.clear()
        try:
            if isinstance(data, dict):
                root_item = QTreeWidgetItem(self.tree)
                root_item.setText(0, "root(dict)")
                root_item.setText(1, "dict")
                root_item.setText(2, "")

                for k, v in data.items():
                    insert_to_tree(self.tree, root_item, k, v)
                root_item.setExpanded(True)

            elif isinstance(data, list):
                root_item = QTreeWidgetItem(self.tree)
                root_item.setText(0, f"root(list[{len(data)}])")
                root_item.setText(1, "list")
                root_item.setText(2, "")

                for i, v in enumerate(data):
                    insert_to_tree(self.tree, root_item, f"[{i}]", v)
                root_item.setExpanded(True)

            else:
                root_item = QTreeWidgetItem(self.tree)
                root_item.setText(0, "root(value)")
                root_item.setText(1, type(data).__name__)
                root_item.setText(2, str(data))

        except Exception as e:
            QMessageBox.critical(self, "Tree error", str(e))

    def show_tab_json(self):
        self.notebook.setCurrentWidget(self.frame_json)

    def show_tab_tree(self):
        self.notebook.setCurrentWidget(self.frame_tree)

    # --- Clear ---
    def clear_input(self):
        self.input_box.clear()

    def clear_output(self):
        self.output_box.clear()
        self.tree.clear()

    # --- Search ops ---
    def _target_text(self):
        return self.input_box if self.target_var == "input" else self.output_box

    def on_highlight_all(self):
        txt = self._target_text()
        highlight_all(txt, self.search_var, self.case_var)

    def on_find_next(self):
        txt = self._target_text()
        # highlight handle
        if not hasattr(txt, "_search_matches") or not txt._search_matches:
            highlight_all(txt, self.search_var, self.case_var)
        else:
            find_next(txt, self.search_var, self.case_var)

    def on_find_prev(self):
        txt = self._target_text()
        if not hasattr(txt, "_search_matches") or not txt._search_matches:
            highlight_all(txt, self.search_var, self.case_var)
        else:
            find_prev(txt, self.search_var, self.case_var)

    def on_clear_highlight(self):
        clear_highlight(self._target_text())


def main():
    app = QApplication(sys.argv)
    window = AppUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
