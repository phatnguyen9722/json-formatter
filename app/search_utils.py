from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat
from PySide6.QtCore import Qt

TAG = "search_match"


def setup_highlight(text_widget: QTextEdit):
    """Setup highlight format for text widget."""
    # Store the default format for later use
    if not hasattr(text_widget, "_default_format"):
        cursor = text_widget.textCursor()
        text_widget._default_format = cursor.charFormat()

    # Create highlight format
    highlight_format = QTextCharFormat()
    highlight_format.setBackground(QColor("#ffee58"))  # Yellow highlight
    text_widget._highlight_format = highlight_format


def clear_highlight(text_widget: QTextEdit):
    """Clear all highlights from text widget."""
    if not hasattr(text_widget, "_search_matches"):
        return

    # Remove all highlights by restoring original formatting
    cursor = text_widget.textCursor()
    cursor.select(QTextCursor.Document)

    # Restore default format
    if hasattr(text_widget, "_default_format"):
        cursor.setCharFormat(text_widget._default_format)

    # Clear search matches
    text_widget._search_matches = []
    text_widget._current_match_index = -1


def highlight_all(text_widget: QTextEdit, pattern: str, case_sensitive=False):
    """Highlight all occurrences of pattern in text widget."""
    clear_highlight(text_widget)
    if not pattern:
        return 0

    document = text_widget.document()
    cursor = QTextCursor(document)
    matches = []

    # Set search flags
    flags = QTextCursor.FindFlags()
    if not case_sensitive:
        flags |= QTextCursor.FindCaseSensitively

    # Find all occurrences
    cursor.movePosition(QTextCursor.Start)
    while True:
        cursor = document.find(pattern, cursor, flags)
        if cursor.isNull():
            break

        # Store match position
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        matches.append((start_pos, end_pos))

        # Move cursor past this match
        cursor.setPosition(end_pos)

    # Apply highlights
    if matches:
        highlight_format = getattr(text_widget, "_highlight_format", QTextCharFormat())
        if not hasattr(text_widget, "_highlight_format"):
            highlight_format.setBackground(QColor("#ffee58"))

        for start_pos, end_pos in matches:
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.setCharFormat(highlight_format)

    # Store matches for navigation
    text_widget._search_matches = matches
    text_widget._current_match_index = -1

    # Navigate to first match
    if matches:
        cursor.setPosition(matches[0][0])
        text_widget.setTextCursor(cursor)

    return len(matches)


def find_next(text_widget: QTextEdit, pattern: str, case_sensitive=False):
    """Find and navigate to next occurrence."""
    if not pattern:
        return

    # If no matches exist, highlight all first
    if not hasattr(text_widget, "_search_matches") or not text_widget._search_matches:
        highlight_all(text_widget, pattern, case_sensitive)
        return

    matches = text_widget._search_matches
    if not matches:
        return

    # Move to next match
    text_widget._current_match_index = (text_widget._current_match_index + 1) % len(
        matches
    )
    current_match = matches[text_widget._current_match_index]

    # Navigate to match
    cursor = text_widget.textCursor()
    cursor.setPosition(current_match[0])
    text_widget.setTextCursor(cursor)


def find_prev(text_widget: QTextEdit, pattern: str, case_sensitive=False):
    """Find and navigate to previous occurrence."""
    if not pattern:
        return

    # If no matches exist, highlight all first
    if not hasattr(text_widget, "_search_matches") or not text_widget._search_matches:
        highlight_all(text_widget, pattern, case_sensitive)
        return

    matches = text_widget._search_matches
    if not matches:
        return

    # Move to previous match
    text_widget._current_match_index = (text_widget._current_match_index - 1) % len(
        matches
    )
    current_match = matches[text_widget._current_match_index]

    # Navigate to match
    cursor = text_widget.textCursor()
    cursor.setPosition(current_match[0])
    text_widget.setTextCursor(cursor)
