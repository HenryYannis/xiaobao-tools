"""局域网文件共享：令牌校验和上传重名测试（不需要图形界面）"""
import http.client
import importlib.util
import os
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path

# 测试环境不一定有图形界面，用空模块代替 tkinter，只测试 HTTP 部分
if "tkinter" not in sys.modules:
    tk = types.ModuleType("tkinter")
    tk.filedialog = types.ModuleType("tkinter.filedialog")
    tk.messagebox = types.ModuleType("tkinter.messagebox")
    sys.modules.update({"tkinter": tk, "tkinter.filedialog": tk.filedialog, "tkinter.messagebox": tk.messagebox})

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lan_file_share", ROOT / "network" / "LAN-File-Share" / "lan_file_share.py")
lfs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lfs)

TOKEN = "abc123"


class LanShareTokenTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        Path(self.dir, "secret.txt").write_text("hello", encoding="utf-8")
        os.mkdir(os.path.join(self.dir, "sub"))
        share_dir = self.dir

        class Handler(lfs.CustomHTTPRequestHandler):
            access_token = TOKEN

            def __init__(self, *a, **kw):
                super().__init__(*a, directory=share_dir, **kw)

            def log_message(self, *a):
                pass

        self.server = lfs.SharingServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def get(self, path, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.request("GET", path, headers=headers or {})
        r = c.getresponse()
        body = r.read()
        c.close()
        return r, body

    def test_file_download_requires_token(self):
        r, _ = self.get("/secret.txt")
        self.assertEqual(r.status, 403)

    def test_partial_or_prefixed_token_rejected(self):
        for q in ("?token=abc123XYZ", "?xtoken=abc123", "?token=abc", "?a=1&token=wrong"):
            r, _ = self.get("/secret.txt" + q)
            self.assertEqual(r.status, 403, q)

    def test_correct_token_allows_and_sets_cookie(self):
        r, body = self.get("/secret.txt?token=" + TOKEN)
        self.assertEqual(r.status, 200)
        self.assertEqual(body, b"hello")
        self.assertIn("access_token=" + TOKEN, r.getheader("Set-Cookie", ""))

    def test_cookie_allows_subdirectory(self):
        r, _ = self.get("/sub/", headers={"Cookie": "access_token=" + TOKEN})
        self.assertEqual(r.status, 200)
        r, _ = self.get("/sub/", headers={"Cookie": "access_token=wrong"})
        self.assertEqual(r.status, 403)

    def test_upload_does_not_overwrite(self):
        boundary = "XyZ"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"secret.txt\"\r\n"
                f"Content-Type: text/plain\r\n\r\nnew\r\n--{boundary}--\r\n").encode()
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.request("POST", "/?token=" + TOKEN, body=body,
                  headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))})
        r = c.getresponse()
        r.read()
        c.close()
        self.assertEqual(r.status, 200)
        self.assertEqual(Path(self.dir, "secret.txt").read_text(encoding="utf-8"), "hello")
        self.assertEqual(Path(self.dir, "secret (1).txt").read_text(encoding="utf-8"), "new")


if __name__ == "__main__":
    unittest.main()
