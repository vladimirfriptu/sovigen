from pathlib import Path

VIDEO_FILTER = (
    "scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
    "format=yuv420p"
)


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
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        "-movflags", "+faststart",
        "-y",
        str(output),
    ]
