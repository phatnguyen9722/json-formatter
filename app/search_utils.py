import tkinter as tk

TAG = "search_match"


def setup_highlight(text_widget: tk.Text):
    text_widget.tag_configure(TAG, background="#ffee58")


def clear_highlight(text_widget: tk.Text):
    text_widget.tag_remove(TAG, "1.0", tk.END)


def highlight_all(text_widget: tk.Text, pattern: str, case_sensitive=False):
    clear_highlight(text_widget)
    if not pattern:
        return 0
    start = "1.0"
    count = 0
    while True:
        pos = text_widget.search(
            pattern, start, stopindex=tk.END, nocase=0 if case_sensitive else 1
        )
        if not pos:
            break
        end = f"{pos}+{len(pattern)}c"
        text_widget.tag_add(TAG, pos, end)
        start = end
        count += 1
    if count:
        first = text_widget.tag_nextrange(TAG, "1.0")
        if first:
            text_widget.see(first[0])
            text_widget.mark_set(tk.INSERT, first[1])
    return count


def find_next(text_widget: tk.Text, pattern: str, case_sensitive=False):
    if not pattern:
        return
    idx = text_widget.index(tk.INSERT)
    pos = text_widget.search(
        pattern, idx, stopindex=tk.END, nocase=0 if case_sensitive else 1
    )
    if not pos:
        pos = text_widget.search(
            pattern, "1.0", stopindex=tk.END, nocase=0 if case_sensitive else 1
        )
        if not pos:
            return
    end = f"{pos}+{len(pattern)}c"
    text_widget.see(pos)
    text_widget.mark_set(tk.INSERT, end)


def find_prev(text_widget: tk.Text, pattern: str, case_sensitive=False):
    if not pattern:
        return
    # get all match, then place before INSERT
    matches = []
    start = "1.0"
    while True:
        pos = text_widget.search(
            pattern, start, stopindex=tk.END, nocase=0 if case_sensitive else 1
        )
        if not pos:
            break
        end = f"{pos}+{len(pattern)}c"
        matches.append((pos, end))
        start = end
    if not matches:
        return
    idx = text_widget.index(tk.INSERT)
    prev = [m for m in matches if text_widget.compare(m[1], "<", idx)]
    target = prev[-1] if prev else matches[-1]
    text_widget.see(target[0])
    text_widget.mark_set(tk.INSERT, target[0])
