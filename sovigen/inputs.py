from pathlib import Path

AUDIO_EXTS = {".mp3"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class InputError(Exception):
    pass


class MissingInputError(InputError):
    pass


class AmbiguousInputError(InputError):
    pass


def _find_single(song_dir: Path, exts: set, kind: str) -> Path:
    matches = []
    for entry in sorted(song_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in exts:
            matches.append(entry)
    if len(matches) == 0:
        raise MissingInputError(f"No {kind} found in {song_dir}")
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        raise AmbiguousInputError(f"Multiple {kind} files in {song_dir}: {names}")
    return matches[0]


def find_audio(song_dir: Path) -> Path:
    return _find_single(song_dir, AUDIO_EXTS, "audio (.mp3)")


def find_image(song_dir: Path) -> Path:
    return _find_single(song_dir, IMAGE_EXTS, "image")
