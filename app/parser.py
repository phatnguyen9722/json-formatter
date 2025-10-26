import json, ast, re


def safe_parse(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None

    # 1) JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2) Python literal
    try:
        return ast.literal_eval(raw)
    except Exception:
        pass

    # 3) Handle for strange object <...> → "..."
    cleaned = re.sub(r"<[^>]+>", lambda m: f'"{m.group(0)}"', raw)

    # 3a) Retry literal
    try:
        return ast.literal_eval(cleaned)
    except Exception:
        pass

    # 3b) True/False/None, ' → " rồi thử JSON
    tmp = cleaned
    tmp = re.sub(r"(?<![A-Za-z0-9_])True(?![A-Za-z0-9_])", "true", tmp)
    tmp = re.sub(r"(?<![A-Za-z0-9_])False(?![A-Za-z0-9_])", "false", tmp)
    tmp = re.sub(r"(?<![A-Za-z0-9_])None(?![A-Za-z0-9_])", "null", tmp)
    tmp = tmp.replace("'", '"')
    try:
        return json.loads(tmp)
    except Exception:
        return raw
