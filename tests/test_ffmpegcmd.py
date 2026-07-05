from pathlib import Path

from sovigen.ffmpegcmd import build_static_video_cmd


def test_cmd_starts_with_ffmpeg_and_inputs():
    cmd = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"))
    assert cmd[0] == "ffmpeg"
    assert "c.jpg" in cmd
    assert "t.mp3" in cmd
    assert cmd[-1] == "out.mp4"


def test_cmd_has_youtube_encoding_flags():
    cmd = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"))
    joined = " ".join(cmd)
    assert "libx264" in cmd
    assert "stillimage" in cmd
    assert "aac" in cmd
    assert "320k" in cmd
    assert "-shortest" in cmd
    assert "1920:1080" in joined
    assert "yuv420p" in joined
