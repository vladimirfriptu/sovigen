import json
from pathlib import Path

META_VERSION = 2
META_FILENAME = "meta.json"

STAGES = [
    "idea",
    "brief",
    "lyrics",
    "prompted",
    "recorded",
    "ready",
    "pre-published",
    "published",
]

LEGACY_STAGES = {"draft": "idea"}


def new_meta(
    title: str,
    slug: str,
    created: str,
    *,
    source=None,
    series=None,
    language: str = "uk",
) -> dict:
    return {
        "meta_version": META_VERSION,
        "title": title,
        "slug": slug,
        "stage": "idea",
        "created": created,
        "source": source,
        "series": series,
        "language": language,
        "style": None,
        "suno_takes": 0,
        "stage_history": [{"stage": "idea", "at": created}],
    }


def meta_path(song_dir: Path) -> Path:
    return song_dir / META_FILENAME


def has_meta(song_dir: Path) -> bool:
    return meta_path(song_dir).exists()


def read_meta(song_dir: Path) -> dict:
    path = meta_path(song_dir)
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    return _normalize(data)


def _normalize(data: dict) -> dict:
    normalized = dict(data)
    stage = normalized.get("stage")
    if stage in LEGACY_STAGES:
        normalized["stage"] = LEGACY_STAGES[stage]
    normalized.setdefault("source", None)
    normalized.setdefault("series", None)
    normalized.setdefault("language", "uk")
    normalized.setdefault("style", None)
    normalized.setdefault("suno_takes", 0)
    normalized.setdefault("stage_history", [])
    normalized["meta_version"] = META_VERSION
    return normalized


def write_meta(song_dir: Path, meta: dict) -> None:
    path = meta_path(song_dir)
    text = json.dumps(meta, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def set_stage(song_dir: Path, stage: str, at: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    data = read_meta(song_dir)
    data["stage"] = stage
    data["stage_history"] = list(data["stage_history"]) + [{"stage": stage, "at": at}]
    write_meta(song_dir, data)


def next_stage(stage: str):
    index = STAGES.index(stage)
    if index + 1 >= len(STAGES):
        return None
    return STAGES[index + 1]
