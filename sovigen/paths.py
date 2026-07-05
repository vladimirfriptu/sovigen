import os
from pathlib import Path


def library_dir() -> Path:
    override = os.environ.get("SOVIGEN_LIBRARY")
    if override:
        return Path(override)
    return Path("library")


def song_dir(slug: str) -> Path:
    base = library_dir()
    return base / slug


def list_song_slugs() -> list[str]:
    base = library_dir()
    if not base.exists():
        return []
    slugs = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir():
            slugs.append(entry.name)
    return slugs
