import datetime
import os
import shutil
import subprocess
from pathlib import Path

from . import artifacts
from . import meta as meta_mod
from . import paths
from .artifacts import AUDIO_FILENAME, VIDEO_FILENAME
from .ffmpegcmd import build_static_video_cmd
from .inputs import AUDIO_EXTS, IMAGE_EXTS, find_audio, find_image
from .slug import slugify


class CommandError(Exception):
    pass


def _read_meta_or_fail(slug: str, song_dir: Path) -> dict:
    if not meta_mod.has_meta(song_dir):
        raise CommandError(f"{slug} has no meta.json")
    try:
        return meta_mod.read_meta(song_dir)
    except (ValueError, OSError) as err:
        raise CommandError(f"cannot read {slug}/meta.json: {err}") from err


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
    data = _read_meta_or_fail(slug, sdir)
    stage = data.get("stage", "?")
    if stage != "ready":
        raise CommandError(
            f"cannot build {slug}: stage is {stage}, expected ready. "
            "Use advance to get the song to ready first."
        )
    output = sdir / VIDEO_FILENAME
    if output.exists():
        raise CommandError(f"{VIDEO_FILENAME} already exists for {slug}")
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
        try:
            data = meta_mod.read_meta(sdir)
        except (ValueError, OSError):
            continue
        if data.get("stage") == "ready":
            cmd_build(slug)
            built.append(slug)
    return built


def cmd_advance(slug: str) -> tuple:
    sdir = _require_song(slug)
    data = _read_meta_or_fail(slug, sdir)
    current = data.get("stage")
    if current not in meta_mod.STAGES:
        known = ", ".join(meta_mod.STAGES)
        raise CommandError(
            f"unknown stage {current!r} in {slug}/meta.json; expected one of: {known}"
        )
    # Legacy songs predate the templates, so give them their scaffolding before
    # asking which artifact is missing. render() leaves existing files alone.
    artifacts.render(sdir, data)
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


def cmd_import(slug: str, src) -> Path:
    sdir = _require_song(slug)
    source = Path(src)
    if not source.is_file():
        raise CommandError(f"File not found: {source}")
    song_root = sdir.resolve()
    if song_root in source.resolve().parents:
        raise CommandError(
            f"{source} is already inside {sdir}; import only brings files in from "
            "outside. Rename it by hand if it needs a canonical name."
        )
    ext = source.suffix.lower()
    if ext in AUDIO_EXTS:
        dest = sdir / AUDIO_FILENAME
        exts = AUDIO_EXTS
    elif ext in IMAGE_EXTS:
        dest = sdir / f"cover{ext}"
        exts = IMAGE_EXTS
    else:
        raise CommandError(f"unsupported file type: {ext or source.name}")
    # Copy first, stash second, rename last: a failed copy must leave the song
    # untouched, and the partial file must never look like a media file.
    staging = sdir / f".sovigen-import-{dest.name}.part"
    try:
        shutil.copy2(source, staging)
        _stash_existing(sdir, exts)
        os.replace(staging, dest)
    except OSError as err:
        staging.unlink(missing_ok=True)
        raise CommandError(f"could not import {source} into {slug}: {err}") from err
    return dest


def _stash_existing(song_dir: Path, exts: set) -> None:
    raw_dir = song_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    for entry in sorted(song_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in exts:
            entry.rename(_free_name(raw_dir, entry.name))


def _free_name(raw_dir: Path, name: str) -> Path:
    candidate = raw_dir / name
    if not candidate.exists():
        return candidate
    stem = Path(name).stem
    suffix = Path(name).suffix
    counter = 2
    while True:
        candidate = raw_dir / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


TURN_BY_STAGE = {
    "idea": "claude",
    "brief": "claude",
    "lyrics": "claude",
    "prompted": "you",
    "recorded": "claude",
    "ready": "claude",
    "pre-published": "you",
    "published": "-",
}


def cmd_status() -> list:
    rows = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        row = {"slug": slug, "stage": "?", "title": slug, "turn": "-"}
        if meta_mod.has_meta(sdir):
            try:
                data = meta_mod.read_meta(sdir)
            except (ValueError, OSError) as err:
                row["stage"] = "unreadable"
                row["error"] = str(err)
                rows.append(row)
                continue
            row["stage"] = data.get("stage", "?")
            row["title"] = data.get("title", slug)
            row["turn"] = TURN_BY_STAGE.get(row["stage"], "-")
        rows.append(row)
    return rows
