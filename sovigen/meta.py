import json
from pathlib import Path

STAGES = ["draft", "ready", "pre-published", "published"]
META_FILENAME = "meta.json"


def new_meta(title: str, slug: str, created: str) -> dict:
    return {"title": title, "slug": slug, "stage": "draft", "created": created}


def meta_path(song_dir: Path) -> Path:
    return song_dir / META_FILENAME


def has_meta(song_dir: Path) -> bool:
    return meta_path(song_dir).exists()


def read_meta(song_dir: Path) -> dict:
    path = meta_path(song_dir)
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def write_meta(song_dir: Path, meta: dict) -> None:
    path = meta_path(song_dir)
    text = json.dumps(meta, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def set_stage(song_dir: Path, stage: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    data = read_meta(song_dir)
    data["stage"] = stage
    write_meta(song_dir, data)
