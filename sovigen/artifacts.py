from pathlib import Path

AUDIO = "audio (.mp3)"
IMAGE = "image"

AUDIO_FILENAME = "track.mp3"
VIDEO_FILENAME = "youtube.mp4"

ARTIFACT_FILES = [
    "brief.md",
    "lyrics.md",
    "suno.md",
    "cover-prompt.md",
    "youtube.md",
    "notes.md",
]

STAGE_REQUIREMENTS = {
    "idea": [],
    "brief": ["brief.md"],
    "lyrics": ["lyrics.md"],
    "prompted": ["suno.md"],
    "recorded": [AUDIO],
    "ready": [IMAGE, "youtube.md"],
    "pre-published": [VIDEO_FILENAME],
    "published": [],
}

VARIANTS_DIRNAME = "variants"

# Only these two fan out into variants/<id>/. The cover, the YouTube metadata
# and the notes belong to the song, not to one reading of it.
FANOUT_FILES = ("lyrics.md", "suno.md")

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def variants_dir(song_dir: Path) -> Path:
    return song_dir / VARIANTS_DIRNAME


def variant_dir(song_dir: Path, variant_id: str) -> Path:
    return variants_dir(song_dir) / variant_id


def variant_ids(song_dir: Path) -> list:
    base = variants_dir(song_dir)
    if not base.is_dir():
        return []
    return sorted(entry.name for entry in base.iterdir() if entry.is_dir())


def _fanout_present(song_dir: Path, name: str) -> bool:
    if (song_dir / name).exists():
        return True
    return any(
        (variant_dir(song_dir, variant_id) / name).exists()
        for variant_id in variant_ids(song_dir)
    )


def render(song_dir: Path, data: dict) -> list:
    values = {
        "title": data.get("title", ""),
        "slug": data.get("slug", ""),
        "source": data.get("source") or "-",
        "series": data.get("series") or "-",
        "language": data.get("language") or "-",
        "created": data.get("created", ""),
    }
    created = []
    for name in ARTIFACT_FILES:
        target = song_dir / name
        if target.exists():
            continue
        template = (_TEMPLATES_DIR / name).read_text(encoding="utf-8")
        target.write_text(template.format_map(values), encoding="utf-8")
        created.append(target)
    return created


def is_scaffolded(song_dir: Path) -> bool:
    return any((song_dir / name).exists() for name in ARTIFACT_FILES)


def missing_for_stage(song_dir: Path, stage: str) -> list:
    from .inputs import AmbiguousInputError, MissingInputError, find_audio, find_image

    finders = {AUDIO: find_audio, IMAGE: find_image}
    missing = []
    for requirement in STAGE_REQUIREMENTS.get(stage, []):
        finder = finders.get(requirement)
        if finder is not None:
            try:
                finder(song_dir)
            except MissingInputError:
                missing.append(requirement)
            except AmbiguousInputError as err:
                missing.append(str(err))
            continue
        if requirement in FANOUT_FILES:
            # The plain name is reported either way: callers parse
            # "missing: lyrics.md" and must not learn a second vocabulary.
            if not _fanout_present(song_dir, requirement):
                missing.append(requirement)
            continue
        if not (song_dir / requirement).exists():
            missing.append(requirement)
    return missing
