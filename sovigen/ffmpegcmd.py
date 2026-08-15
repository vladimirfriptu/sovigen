from pathlib import Path

# in_range=auto, not full: a JPEG cover decodes as full-range yuvj420p, a PNG as
# RGB, and only the JPEG needs compressing to tv levels. Forcing full would wash
# out every PNG cover the library already has.
VIDEO_FILTER = (
    "scale=1920:1080:force_original_aspect_ratio=decrease"
    ":in_range=auto:out_range=tv,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
    "format=yuv420p"
)

ACCENT = "0xE8B96A"


def build_static_video_cmd(image: Path, audio: Path, output: Path) -> list:
    return [
        "ffmpeg",
        "-loop", "1",
        "-framerate", "2",
        "-i", str(image),
        "-i", str(audio),
        "-vf", VIDEO_FILTER,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-r", "24",
        "-pix_fmt", "yuv420p",
        "-color_range", "tv",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        "-movflags", "+faststart",
        "-y",
        str(output),
    ]


def probe_duration_cmd(audio: Path) -> list:
    return [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(audio),
    ]


def build_spectrum_video_cmd(
    image: Path, audio: Path, output: Path, duration: float
) -> list:
    # The background is scrimmed before the line is drawn: a spectrum line over
    # a bright cover reads as noise otherwise.
    background = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
        "format=rgba,"
        "drawbox=x=0:y=ih-200:w=iw:h=200:color=black@0.25:t=fill,"
        "drawbox=x=0:y=ih-8:w=iw:h=8:color=black@0.45:t=fill,"
        f"drawbox=x=0:y=ih-8:w='iw*t/{duration}':h=8:color={ACCENT}@0.95:t=fill[bg]"
    )
    line = (
        "[1:a]showfreqs=s=1920x150:mode=line:ascale=log:fscale=log:"
        f"win_size=2048:averaging=6:colors={ACCENT}|{ACCENT},format=rgba[w]"
    )
    # showfreqs colours each channel separately, so both channels get the accent
    # explicitly; leaving the second one default paints it green.
    # JPEG covers arrive full-range and the flag leaks into the stream as
    # yuvj420p, which shifts contrast in some players; pin it back to tv range.
    compose = (
        "[bg][w]overlay=0:H-170,format=yuv420p,"
        "scale=in_range=full:out_range=tv[out]"
    )
    graph = ";".join([background, line, compose])
    return [
        "ffmpeg",
        "-loop", "1",
        "-framerate", "24",
        "-i", str(image),
        "-i", str(audio),
        "-filter_complex", graph,
        "-map", "[out]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-r", "24",
        "-pix_fmt", "yuv420p",
        "-color_range", "tv",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        "-movflags", "+faststart",
        "-y",
        str(output),
    ]
