import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

EXTENSION_ORIGIN_PREFIX = "chrome-extension://"


class Bridge:
    def __init__(self, port: int = 8787):
        self._queue = []
        self._results = {}
        self._events = {}
        self._lock = threading.Lock()
        self._extension_seen = threading.Event()
        self._server = ThreadingHTTPServer(("127.0.0.1", port), self._make_handler())
        self.port = self._server.server_address[1]
        self._thread = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def submit(self, job: dict) -> str:
        job_id = uuid.uuid4().hex
        with self._lock:
            self._queue.append({**job, "id": job_id})
            self._events[job_id] = threading.Event()
        return job_id

    def wait_result(self, job_id: str, timeout: float):
        event = self._events[job_id]
        if not event.wait(timeout):
            return None
        return self._results[job_id]

    def wait_for_extension(self, timeout: float) -> bool:
        return self._extension_seen.wait(timeout)

    def _next_job(self):
        self._extension_seen.set()
        with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)

    def _store_result(self, result: dict) -> None:
        job_id = result.get("id")
        with self._lock:
            event = self._events.get(job_id)
            if event is None:
                return
            self._results[job_id] = result
        event.set()

    def _make_handler(self):
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status: int, body: bytes = b"") -> None:
                self.send_response(status)
                origin = self.headers.get("Origin", "")
                if origin.startswith(EXTENSION_ORIGIN_PREFIX):
                    self.send_header("Access-Control-Allow-Origin", origin)
                    self.send_header("Access-Control-Allow-Headers", "Content-Type")
                    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Content-Length", str(len(body)))
                if body:
                    self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):
                self._send(204)

            def do_GET(self):
                if self.path != "/job":
                    self._send(404)
                    return
                job = bridge._next_job()
                if job is None:
                    self._send(204)
                    return
                self._send(200, json.dumps(job, ensure_ascii=False).encode("utf-8"))

            def do_POST(self):
                if self.path != "/result":
                    self._send(404)
                    return
                length = int(self.headers.get("Content-Length", 0))
                try:
                    result = json.loads(self.rfile.read(length) or b"{}")
                except ValueError:
                    self._send(400)
                    return
                bridge._store_result(result)
                self._send(200)

        return Handler
