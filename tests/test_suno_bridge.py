import json
import urllib.request

import pytest

from sovigen.suno_bridge import Bridge


@pytest.fixture
def bridge():
    b = Bridge(port=0)
    b.start()
    yield b
    b.stop()


def _get(bridge, path="/job"):
    return urllib.request.urlopen(f"http://127.0.0.1:{bridge.port}{path}")


def _post(bridge, body):
    req = urllib.request.Request(
        f"http://127.0.0.1:{bridge.port}/result",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return urllib.request.urlopen(req)


def test_get_job_empty_returns_204(bridge):
    assert _get(bridge).status == 204


def test_job_is_returned_once(bridge):
    bridge.submit({"variant": "a"})
    first = _get(bridge)
    assert first.status == 200
    assert json.loads(first.read())["variant"] == "a"
    assert _get(bridge).status == 204


def test_jobs_come_in_submit_order(bridge):
    bridge.submit({"variant": "a"})
    bridge.submit({"variant": "b"})
    assert json.loads(_get(bridge).read())["variant"] == "a"
    assert json.loads(_get(bridge).read())["variant"] == "b"


def test_post_result_unblocks_wait_result(bridge):
    job_id = bridge.submit({"variant": "a"})
    _get(bridge)
    _post(bridge, {"id": job_id, "ok": True, "clips": 2, "error": ""})
    result = bridge.wait_result(job_id, timeout=2)
    assert result["ok"] is True
    assert result["clips"] == 2


def test_result_for_unknown_id_is_ignored(bridge):
    assert _post(bridge, {"id": "nope", "ok": True}).status == 200


def test_wait_result_times_out_returns_none(bridge):
    job_id = bridge.submit({"variant": "a"})
    assert bridge.wait_result(job_id, timeout=0.1) is None


def test_wait_for_extension_false_when_nobody_polls(bridge):
    assert bridge.wait_for_extension(timeout=0.1) is False


def test_wait_for_extension_true_after_first_get(bridge):
    _get(bridge)
    assert bridge.wait_for_extension(timeout=1) is True


def test_unknown_path_is_404(bridge):
    with pytest.raises(urllib.error.HTTPError) as err:
        _get(bridge, "/other")
    assert err.value.code == 404


def test_extension_offline_before_any_poll(bridge):
    assert bridge.extension_online(max_age=10) is False


def test_extension_online_right_after_a_poll(bridge):
    _get(bridge)
    assert bridge.extension_online(max_age=10) is True


def test_extension_goes_offline_when_polls_stop(bridge):
    _get(bridge)
    assert bridge.extension_online(max_age=0) is False
