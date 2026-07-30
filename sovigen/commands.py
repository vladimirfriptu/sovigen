import datetime
import subprocess
from pathlib import Path

from . import artifacts
from . import meta as meta_mod
from . import paths
from .ffmpegcmd import build_static_video_cmd
from .inputs import find_audio, find_image
from .slug import slugify

OUTPUT_FILENAME = "youtube.mp4"


class CommandError(Exception):
    pass


def _require_song(slug: str) -> Path:
    sdir = paths.song_dir(slug)
    if not sdir.is_dir():
        available = ", ".join(paths.list_song_slugs()) or "(none)"
        raise CommandError(f"Song not found: {slug}. Available: {available}")
    return sdir


def cmd_new(title: str, *, source=None, series=None, language: str = "uk") -> Path:
    slug = slugify(title)
    if not slug:
        raise CommandError(f"Could not derive a slug from title: {title!r}")
    sdir = paths.song_dir(slug)
    if sdir.exists():
        raise CommandError(f"Song already exists: {slug}")
    raw_dir = sdir / "raw"
    raw_dir.mkdir(parents=True)
    today = datetime.date.today().isoformat()
    data = meta_mod.new_meta(
        title, slug, today, source=source, series=series, language=language
    )
    meta_mod.write_meta(sdir, data)
    artifacts.render(sdir, data)
    return sdir


def cmd_build(slug: str) -> Path:
    sdir = _require_song(slug)
    output = sdir / OUTPUT_FILENAME
    if output.exists():
        raise CommandError(f"{OUTPUT_FILENAME} already exists for {slug}")
    image = find_image(sdir)
    audio = find_audio(sdir)
    cmd = build_static_video_cmd(image, audio, output)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise CommandError(f"ffmpeg failed for {slug}:\n{result.stderr}")
    meta_mod.set_stage(sdir, "pre-published", datetime.date.today().isoformat())
    return output


def cmd_build_all() -> list:
    built = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        if not meta_mod.has_meta(sdir):
            continue
        data = meta_mod.read_meta(sdir)
        if data.get("stage") == "ready":
            cmd_build(slug)
            built.append(slug)
    return built


def cmd_advance(slug: str) -> tuple:
    sdir = _require_song(slug)
    data = meta_mod.read_meta(sdir)
    current = data["stage"]
    target = meta_mod.next_stage(current)
    if target is None:
        return (current, current)
    missing = artifacts.missing_for_stage(sdir, target)
    if missing:
        raise CommandError(
            f"cannot advance {slug} to {target}, missing: " + ", ".join(missing)
        )
    today = datetime.date.today().isoformat()
    meta_mod.set_stage(sdir, target, today)
    return (current, target)


def cmd_publish(slug: str) -> None:
    sdir = _require_song(slug)
    today = datetime.date.today().isoformat()
    meta_mod.set_stage(sdir, "published", today)


def cmd_status() -> list:
    rows = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        row = {"slug": slug, "stage": "?", "title": slug}
        if meta_mod.has_meta(sdir):
            data = meta_mod.read_meta(sdir)
            row["stage"] = data.get("stage", "?")
            row["title"] = data.get("title", slug)
        rows.append(row)
    return rows
