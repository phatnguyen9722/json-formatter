def insert_to_tree(tree, parent, key, value, max_len=200):
    """
    Recursively inserts a JSON-like data structure into a ttk.Treeview widget.

    This function traverses through dictionaries, lists, and primitive values,
    creating a hierarchical tree representation where each node shows the key
    and type information, with leaf nodes also displaying the value.

    Args:
        tree: A ttk.Treeview widget instance where the data will be inserted
        parent: The parent tree item ID (string) under which to insert the current item
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
        >>> import tkinter as tk
        >>> from tkinter import ttk
        >>> root = tk.Tk()
        >>> tree = ttk.Treeview(root)
        >>> data = {"name": "John", "scores": [85, 90, 95]}
        >>> insert_to_tree(tree, "", "root", data)
    """
    tname = type(value).__name__

    if isinstance(value, dict):
        node = tree.insert(parent, "end", text=str(key), values=(tname, ""))
        for k, v in value.items():
            insert_to_tree(tree, node, k, v, max_len)
    elif isinstance(value, list):
        node = tree.insert(
            parent, "end", text=str(key), values=(f"list[{len(value)}]", "")
        )
        for i, v in enumerate(value):
            insert_to_tree(tree, node, f"[{i}]", v, max_len)
    else:
        s = str(value)
        if len(s) > max_len:
            s = s[:max_len] + "…"
        tree.insert(parent, "end", text=str(key), values=(tname, s))
