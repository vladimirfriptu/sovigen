import re


def slugify(title: str) -> str:
    lowered = title.strip().lower()
    cleaned = re.sub(r"[^\w]+", "-", lowered, flags=re.UNICODE)
    collapsed = re.sub(r"_+", "-", cleaned)
    trimmed = collapsed.strip("-")
    return trimmed
