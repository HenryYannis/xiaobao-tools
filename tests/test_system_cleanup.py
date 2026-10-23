"""系统垃圾清理工具：环境变量为空时不误删当前目录；清理更新缓存出错也会重启更新服务"""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "system" / "System-Cleanup" / "system_cleanup.py"


def load_module():
    if "tkinter" not in sys.modules:
        tk = types.ModuleType("tkinter")
        tk.messagebox = types.ModuleType("tkinter.messagebox")
        tk.filedialog = types.ModuleType("tkinter.filedialog")
        sys.modules.update({"tkinter": tk, "tkinter.messagebox": tk.messagebox, "tkinter.filedialog": tk.filedialog})
    if not hasattr(sys.modules["tkinter"], "ttk"):
        ttk = types.ModuleType("tkinter.ttk")
        sys.modules["tkinter"].ttk = ttk
        sys.modules["tkinter.ttk"] = ttk
    spec = importlib.util.spec_from_file_location("system_cleanup_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SystemCleanupTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        cls = next(v for v in vars(self.mod).values() if isinstance(v, type) and hasattr(v, "cleanup_temp_files"))
        self.app = object.__new__(cls)

    def test_env_dir_rejects_empty_and_relative(self):
        with mock.patch.dict(os.environ, {"LOCALAPPDATA": ""}):
            self.assertIsNone(self.mod._env_dir("LOCALAPPDATA", "Temp"))
        with mock.patch.dict(os.environ, {"LOCALAPPDATA": "relative"}):
            self.assertIsNone(self.mod._env_dir("LOCALAPPDATA", "Temp"))

    def test_temp_cleanup_does_not_touch_cwd(self):
        work = tempfile.mkdtemp()
        os.makedirs(os.path.join(work, "Temp"))
        keep = Path(work, "Temp", "student_work.txt")
        keep.write_text("keep", encoding="utf-8")
        fake_temp = tempfile.mkdtemp()
        Path(fake_temp, "junk.tmp").write_text("x", encoding="utf-8")
        old = os.getcwd()
        os.chdir(work)
        try:
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": ""}), \
                    mock.patch.object(self.mod.tempfile, "gettempdir", return_value=fake_temp):
                self.app.cleanup_temp_files()
        finally:
            os.chdir(old)
        self.assertTrue(keep.exists(), "不能删除当前工作目录下的 Temp 文件夹")
        self.assertFalse(Path(fake_temp, "junk.tmp").exists())

    def test_update_service_restarted_on_error(self):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "SoftwareDistribution", "Download"))
        calls = []
        with mock.patch.dict(os.environ, {"SystemRoot": root}), \
                mock.patch.object(self.mod, "_run_quiet", side_effect=lambda args, **kw: calls.append(args)), \
                mock.patch.object(self.mod.os, "makedirs", side_effect=OSError("boom")):
            self.app.cleanup_update_cache()
        self.assertIn(["net", "stop", "wuauserv"], calls)
        self.assertEqual(calls[-1], ["net", "start", "wuauserv"])

    def test_system_options_need_admin(self):
        self.app.cleanup_options = {"system_logs": {"name": "系统日志"}}
        self.app._skipped_need_admin = []
        with mock.patch.object(self.mod, "_is_admin", return_value=False), \
                mock.patch.object(self.app, "cleanup_system_logs", create=True) as clean:
            self.app.cleanup_by_type("system_logs")
        clean.assert_not_called()
        self.assertEqual(self.app._skipped_need_admin, ["系统日志"])


if __name__ == "__main__":
    unittest.main()
