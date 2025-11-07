from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


def insert_to_tree(tree: QTreeWidget, parent: QTreeWidgetItem, key, value, max_len=200):
    """
    Recursively inserts a JSON-like data structure into a QTreeWidget.

    This function traverses through dictionaries, lists, and primitive values,
    creating a hierarchical tree representation where each node shows the key
    and type information, with leaf nodes also displaying the value.

    Args:
        tree: A QTreeWidget widget instance where the data will be inserted
        parent: The parent QTreeWidgetItem under which to insert the current item
        key: The key or index name for the current item (will be converted to string)
        value: The value to insert - can be dict, list, or any primitive type
        max_len: Maximum length for string representation of primitive values.
                 If longer, the string will be truncated with ellipsis. Defaults to 200.

    Returns:
        None

    Side Effects:
        - Modifies the tree widget by inserting new items
        - Recursively calls itself for nested structures

    Tree Structure:
        - Dict items show as: key | dict | (empty value column)
        - List items show as: key | list[n] | (empty value column) where n is length
        - Primitive items show as: key | type | value (truncated if too long)

    Example:
        >>> from PySide6.QtWidgets import QApplication, QTreeWidget
        >>> app = QApplication([])
        >>> tree = QTreeWidget()
        >>> tree.setHeaderLabels(["Key", "Type", "Value"])
        >>> data = {"name": "John", "scores": [85, 90, 95]}
        >>> insert_to_tree(tree, tree.invisibleRootItem(), "root", data)
    """
    tname = type(value).__name__

    if isinstance(value, dict):
        # Create tree item for dictionary
        if parent is tree.invisibleRootItem():
            node = QTreeWidgetItem(tree)
        else:
            node = QTreeWidgetItem(parent)

        node.setText(0, str(key))
        node.setText(1, tname)
        node.setText(2, "")

        # Add dictionary items as children
        for k, v in value.items():
            insert_to_tree(tree, node, k, v, max_len)

    elif isinstance(value, list):
        # Create tree item for list
        if parent is tree.invisibleRootItem():
            node = QTreeWidgetItem(tree)
        else:
            node = QTreeWidgetItem(parent)

        node.setText(0, str(key))
        node.setText(1, f"list[{len(value)}]")
        node.setText(2, "")

        # Add list items as children
        for i, v in enumerate(value):
            insert_to_tree(tree, node, f"[{i}]", v, max_len)

    else:
        # Create tree item for primitive value
        if parent is tree.invisibleRootItem():
            node = QTreeWidgetItem(tree)
        else:
            node = QTreeWidgetItem(parent)

        s = str(value)
        if len(s) > max_len:
            s = s[:max_len] + "…"

        node.setText(0, str(key))
        node.setText(1, tname)
        node.setText(2, s)
