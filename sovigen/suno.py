import re
import time

from . import meta as meta_mod
from . import paths

STYLE_LIMIT = 1000
LYRICS_LIMIT = 5000
EXTENSION_WAIT_SECONDS = 20
RESULT_WAIT_SECONDS = 330
DEFAULT_PAUSE_SECONDS = 30


class SunoError(Exception):
    pass


def _code_block_after(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        raise SunoError(f"suno.md has no '## {heading}' section")
    rest = text[match.end():]
    block = re.search(r"```[^\n]*\n(.*?)\n```", rest, re.DOTALL)
    if not block:
        raise SunoError(f"'## {heading}' in suno.md has no code block")
    return block.group(1).strip()


def read_variant(slug: str, variant: str) -> dict:
    vdir = paths.song_dir(slug) / "variants" / variant
    suno_path = vdir / "suno.md"
    lyrics_path = vdir / "lyrics.md"
    for path in (suno_path, lyrics_path):
        if not path.is_file():
            raise SunoError(f"missing {path}")

    suno_text = suno_path.read_text(encoding="utf-8")
    style = _code_block_after(suno_text, "Style")
    exclude = _code_block_after(suno_text, "Exclude Styles")

    lyrics_text = lyrics_path.read_text(encoding="utf-8")
    lyrics_text = re.sub(r"\A---\n.*?\n---\n", "", lyrics_text, flags=re.DOTALL)
    lyrics_text = re.sub(r"^# .*\n", "", lyrics_text, count=1, flags=re.MULTILINE)
    lyrics = re.split(r"^## ", lyrics_text, maxsplit=1, flags=re.MULTILINE)[0].strip()

    if len(style) > STYLE_LIMIT:
        raise SunoError(f"Style is {len(style)} chars, Suno allows {STYLE_LIMIT}")
    if len(lyrics) > LYRICS_LIMIT:
        raise SunoError(f"lyrics are {len(lyrics)} chars, Suno allows {LYRICS_LIMIT}")
    return {"lyrics": lyrics, "style": style, "exclude": exclude}


def list_variants(slug: str) -> list:
    vdir = paths.song_dir(slug) / "variants"
    if not vdir.is_dir():
        raise SunoError(f"{slug} has no variants/ folder")
    names = []
    for entry in sorted(vdir.iterdir()):
        has_files = (entry / "suno.md").is_file() and (entry / "lyrics.md").is_file()
        if entry.is_dir() and has_files:
            names.append(entry.name)
    if not names:
        raise SunoError(f"{slug} has no variant with both suno.md and lyrics.md")
    return names


def _bump_suno_takes(slug: str, clips: int) -> None:
    sdir = paths.song_dir(slug)
    meta = meta_mod.read_meta(sdir)
    meta["suno_takes"] += clips
    meta_mod.write_meta(sdir, meta)


def send_to_suno(slug, variants, pause, bridge, sleep=time.sleep) -> list:
    jobs = []
    for variant in variants:
        known = list_variants(slug)
        if variant not in known:
            raise SunoError(f"{slug} has no variant '{variant}' (have: {', '.join(known)})")
        jobs.append((variant, read_variant(slug, variant)))

    if not bridge.wait_for_extension(EXTENSION_WAIT_SECONDS):
        raise SunoError(
            "the extension did not connect: open suno.com/create in Chrome "
            "with the sovigen extension loaded"
        )

    results = []
    for index, (variant, data) in enumerate(jobs):
        if index:
            sleep(pause)
        job_id = bridge.submit({"slug": slug, "variant": variant, **data})
        result = bridge.wait_result(job_id, RESULT_WAIT_SECONDS)
        if result is None:
            result = {"ok": False, "clips": 0, "error": "no answer from the extension"}
        row = {
            "variant": variant,
            "ok": bool(result.get("ok")),
            "clips": int(result.get("clips") or 0),
            "error": result.get("error", ""),
        }
        results.append(row)
        if not row["ok"]:
            break
        _bump_suno_takes(slug, row["clips"])
    return results
