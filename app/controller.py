import json
from .parser import safe_parse
from .encoder import SafeEncoder


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
