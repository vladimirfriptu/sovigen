#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <song-slug>\n' "$0" >&2
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="$1"
cd "$PROJECT_ROOT"

STAGE="$(python3 - "$SLUG" <<'PY'
import sys

from sovigen import meta, paths

slug = sys.argv[1]
song_dir = paths.song_dir(slug)
if not song_dir.is_dir() or not meta.has_meta(song_dir):
    raise SystemExit(f"Song not found: {slug}")
print(meta.read_meta(song_dir).get("stage", "?"))
PY
)"
SONG_DIR="$(python3 - "$SLUG" <<'PY'
import sys

from sovigen import paths

print(paths.song_dir(sys.argv[1]))
PY
)"
OUTPUT="$SONG_DIR/youtube.mp4"
ALREADY_BUILT=0

if [[ "$STAGE" != "pre-published" && -e "$OUTPUT" ]]; then
  printf 'Existing video found; refusing to change the song stage or overwrite it: %s\n' "$OUTPUT" >&2
  exit 1
fi

case "$STAGE" in
  recorded)
    python3 -m sovigen.cli advance "$SLUG"
    ;;
  ready)
    ;;
  pre-published)
    if [[ -f "$OUTPUT" ]]; then
      ALREADY_BUILT=1
    else
      printf 'Song is pre-published but its video is missing: %s\n' "$OUTPUT" >&2
      exit 1
    fi
    ;;
  *)
    printf 'Cannot build from stage %s. Upload the selected Suno track and cover in the studio first.\n' "$STAGE" >&2
    exit 1
    ;;
esac

if [[ "$ALREADY_BUILT" -eq 0 ]]; then
  python3 -m sovigen.cli build "$SLUG" --static
fi

python3 - "$OUTPUT" "$SONG_DIR" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

output, song_dir = Path(sys.argv[1]), Path(sys.argv[2])
video = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0",
    "-show_entries", "stream=width,height,pix_fmt", "-of", "json", str(output),
], text=True))["streams"][0]
duration = float(json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "json", str(output),
], text=True))["format"]["duration"])
audio_files = [p for p in song_dir.iterdir() if p.is_file() and p.suffix.lower() in {".wav", ".m4a", ".mp3"}]
if len(audio_files) != 1:
    raise SystemExit(f"Expected one audio file, found {len(audio_files)}")
audio_duration = float(json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "json", str(audio_files[0]),
], text=True))["format"]["duration"])
if (video["width"], video["height"], video["pix_fmt"]) != (1920, 1080, "yuv420p"):
    raise SystemExit(f"Unexpected video format: {video}")
if abs(duration - audio_duration) > 0.5:
    raise SystemExit(f"Video/audio duration mismatch: {duration:.2f}s / {audio_duration:.2f}s")
print(f"Verified: 1920x1080 yuv420p, {duration:.2f}s, matches {audio_files[0].name}")
PY
printf 'Ready for review: %s\n' "$OUTPUT"
