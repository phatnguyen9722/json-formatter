import json
from tkinter import simpledialog
from .parser import safe_parse
from .encoder import SafeEncoder
from .typeddict_generator import generate_from_json_string


class Controller:
    def __init__(self, ui):
        self.ui = ui

    def convert_pretty(self):
        raw = self.ui.get_input()
        data = safe_parse(raw)
        try:
            pretty = json.dumps(data, indent=2, ensure_ascii=False, cls=SafeEncoder)
        except Exception as e:
            pretty = f"Error dump JSON: {e}\n\nRAW:\n{data}"
        self.ui.set_output(pretty)
        self.ui.show_tab_json()

    def minify(self):
        raw = self.ui.get_input()
        data = safe_parse(raw)
        try:
            mini = json.dumps(
                data, separators=(",", ":"), ensure_ascii=False, cls=SafeEncoder
            )
        except Exception as e:
            mini = f"Error minify JSON: {e}"
        self.ui.set_output(mini)
        self.ui.show_tab_json()

    def build_tree(self):
        raw = self.ui.get_input()
        data = safe_parse(raw)
        self.ui.load_tree(data)
        self.ui.show_tab_tree()

    def generate_typeddict(self):
        """Generate Python TypedDict from JSON input."""
        raw = self.ui.get_input()

        # Ask user for class name
        class_name = simpledialog.askstring(
            "TypedDict Generator",
            "Enter class name for the TypedDict:",
            initialvalue="Product",
        )

        if not class_name:
            return  # User cancelled

        # Generate TypedDict code
        typeddict_code = generate_from_json_string(raw, class_name)
        self.ui.set_output(typeddict_code)
        self.ui.show_tab_json()
