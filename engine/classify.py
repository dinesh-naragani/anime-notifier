def classify(title: str):
    t = title.upper()
    if "1080P" not in t:
        return None
    if "H.265" in t or "X265" in t:
        return "H265"
    if t.startswith("[SUBSPLEASE]") or t.startswith("[ERAI-RAWS]"):
        return "H264"
    return None
