def insert_to_tree(tree, parent, key, value, max_len=200):
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
