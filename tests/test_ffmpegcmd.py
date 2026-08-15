from pathlib import Path

from sovigen.ffmpegcmd import (
    build_spectrum_video_cmd,
    build_static_video_cmd,
    probe_duration_cmd,
)


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


def test_probe_duration_asks_ffprobe_for_a_bare_number():
    cmd = probe_duration_cmd(Path("t.mp3"))
    assert cmd[0] == "ffprobe"
    assert cmd[-1] == "t.mp3"
    assert "format=duration" in cmd


def test_spectrum_cmd_keeps_inputs_and_encoding():
    cmd = build_spectrum_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"), 217.0)
    joined = " ".join(cmd)
    assert cmd[0] == "ffmpeg"
    assert "c.jpg" in cmd
    assert "t.mp3" in cmd
    assert cmd[-1] == "out.mp4"
    assert "libx264" in cmd
    assert "aac" in cmd
    assert "320k" in cmd
    assert "-shortest" in cmd
    assert "1920:1080" in joined


def test_spectrum_cmd_draws_the_line_and_the_progress_bar():
    cmd = build_spectrum_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"), 217.0)
    graph = _filter_graph(cmd)
    assert "showfreqs" in graph
    assert "217.0" in graph, "progress bar must know the track length"


def test_spectrum_cmd_converts_to_yuv_only_at_the_end():
    # Blending an RGBA overlay onto a YUV background swaps colour planes and
    # turns the whole frame purple, so the graph must stay in RGB until the
    # very last step.
    graph = _filter_graph(
        build_spectrum_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"), 217.0)
    )
    assert graph.index("overlay") < graph.index("format=yuv420p")
    assert "format=yuv420p" not in graph[: graph.index("overlay")]


def test_static_and_spectrum_write_the_same_output_name():
    static = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("o.mp4"))
    spectrum = build_spectrum_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("o.mp4"), 1.0)
    assert static[-1] == spectrum[-1]


def _filter_graph(cmd: list) -> str:
    return cmd[cmd.index("-filter_complex") + 1]


def test_spectrum_cmd_pins_the_colour_range():
    cmd = build_spectrum_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"), 217.0)
    assert "tv" in cmd
    assert "out_range=tv" in _filter_graph(cmd)


def test_static_cmd_pins_the_colour_range():
    # A JPEG cover decodes as full-range yuvj420p and that flag leaks into the
    # stream, shifting contrast in some players. The static path must clamp the
    # range the same way the spectrum path already does.
    cmd = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"))
    joined = " ".join(cmd)
    assert "out_range=tv" in joined
    assert "-color_range" in cmd
    assert "-pix_fmt" in cmd
