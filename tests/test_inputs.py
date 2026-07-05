import pytest

from sovigen.inputs import InputError, find_audio, find_image


def _touch(p):
    p.write_bytes(b"")


def test_find_audio_single(tmp_path):
    _touch(tmp_path / "track.mp3")
    assert find_audio(tmp_path) == tmp_path / "track.mp3"


def test_find_audio_none(tmp_path):
    with pytest.raises(InputError):
        find_audio(tmp_path)


def test_find_audio_multiple(tmp_path):
    _touch(tmp_path / "a.mp3")
    _touch(tmp_path / "b.mp3")
    with pytest.raises(InputError):
        find_audio(tmp_path)


def test_find_image_single_case_insensitive(tmp_path):
    _touch(tmp_path / "cover.JPG")
    assert find_image(tmp_path) == tmp_path / "cover.JPG"


def test_find_image_ignores_raw_subdir(tmp_path):
    (tmp_path / "raw").mkdir()
    _touch(tmp_path / "raw" / "a.png")
    _touch(tmp_path / "raw" / "b.png")
    _touch(tmp_path / "cover.png")
    assert find_image(tmp_path) == tmp_path / "cover.png"


def test_find_image_multiple_in_root(tmp_path):
    _touch(tmp_path / "a.png")
    _touch(tmp_path / "b.jpg")
    with pytest.raises(InputError):
        find_image(tmp_path)
