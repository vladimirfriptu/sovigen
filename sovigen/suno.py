import json
import os
import re
import subprocess
import time

from . import paths

CREATE_URL = "https://suno.com/create"
LYRICS_SELECTOR = '[aria-label="Lyrics editor"]'
STYLE_SELECTOR = 'textarea[placeholder^="country metal"]'
EXCLUDE_SELECTOR = 'input[placeholder="Exclude styles"]'
CREATE_BUTTON_SELECTOR = 'button[aria-label="Create song"]'

CLIPS_JS = (
    "JSON.stringify([...new Set([...document.querySelectorAll('a[href^=\"/song/\"]')]"
    ".map(a => a.getAttribute('href')))])"
)
OPEN_MORE_OPTIONS_JS = (
    "(() => { const b = [...document.querySelectorAll('div[role=button]')]"
    ".find(e => e.textContent.trim() === 'More Options'); if (b) b.click(); return !!b; })()"
)

NEW_CLIPS_EXPECTED = 2
CLIPS_TIMEOUT_SECONDS = 120
CLIPS_POLL_SECONDS = 4
STYLE_LIMIT = 1000
LYRICS_LIMIT = 5000

ENV_API_KEY = "NOTTE_API_KEY"
ENV_PROFILE = "SUNO_PROFILE_ID"


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


def _clean_exclude(exclude: str) -> str:
    return exclude.replace("\n", " ").strip()


class Notte:
    def __init__(self, api_key: str, profile_id: str):
        self.env = dict(os.environ)
        self.env["NOTTE_API_KEY"] = api_key
        self.env.setdefault("NOTTE_API_URL", "https://us-prod.notte.cc")
        self.env.setdefault("NOTTE_REQUEST_ORIGIN", "cli")
        self.profile_id = profile_id
        self.session_id = None

    def _run(self, *args: str) -> str:
        proc = subprocess.run(
            ["notte", *args], env=self.env, capture_output=True, text=True
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip()
            raise SunoError(f"notte {args[0]} {args[1]} failed: {detail}")
        return proc.stdout.strip()

    def start(self) -> None:
        out = self._run(
            "sessions", "start", "--profile-id", self.profile_id, "-o", "json"
        )
        self.session_id = json.loads(out)["session_id"]

    def stop(self) -> None:
        if self.session_id:
            self._run("sessions", "stop", "--session-id", self.session_id, "-y")
            self.session_id = None

    def page(self, *args: str) -> str:
        return self._run("page", args[0], "--session-id", self.session_id, *args[1:])

    def eval_js(self, code: str) -> str:
        return self.page("eval-js", code)


def _list_clips(notte: Notte) -> list:
    return json.loads(notte.eval_js(CLIPS_JS))


def _wait_for_new_clips(notte: Notte, before: set) -> list:
    deadline = time.monotonic() + CLIPS_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        new = [href for href in _list_clips(notte) if href not in before]
        if len(new) >= NEW_CLIPS_EXPECTED:
            return new
        time.sleep(CLIPS_POLL_SECONDS)
    raise SunoError(
        f"no new clips after {CLIPS_TIMEOUT_SECONDS}s: Suno may be out of credits, "
        "or the profile is logged out"
    )


def generate(slug: str, variant: str, title: str = None, notte: Notte = None) -> list:
    data = read_variant(slug, variant)

    if notte is None:
        api_key = os.environ.get(ENV_API_KEY)
        profile_id = os.environ.get(ENV_PROFILE)
        if not api_key or not profile_id:
            raise SunoError(f"set {ENV_API_KEY} and {ENV_PROFILE} in the environment")
        notte = Notte(api_key, profile_id)

    notte.start()
    try:
        notte.page("goto", CREATE_URL)
        notte.eval_js(OPEN_MORE_OPTIONS_JS)
        if notte.eval_js("document.querySelector('[aria-label=\"Lyrics editor\"]') !== null") != "true":
            raise SunoError("Suno create form not found: the profile is probably logged out")

        notte.page("fill", LYRICS_SELECTOR, data["lyrics"])
        notte.page("fill", STYLE_SELECTOR, data["style"])
        notte.page("fill", EXCLUDE_SELECTOR, _clean_exclude(data["exclude"]))
        if title:
            notte.page("fill", 'input[placeholder="Song Title (Optional)"]', title)

        before = set(_list_clips(notte))
        notte.page("click", CREATE_BUTTON_SELECTOR)
        new = _wait_for_new_clips(notte, before)
        return ["https://suno.com" + href for href in new]
    finally:
        notte.stop()
