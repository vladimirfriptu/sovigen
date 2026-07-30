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

_TEMPLATES_DIR = Path(__file__).parent / "templates"


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
        if not (song_dir / requirement).exists():
            missing.append(requirement)
    return missing
