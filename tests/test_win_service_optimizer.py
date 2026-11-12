"""Win 服务优化工具：sc 参数格式、中文编码容错与受保护服务注册表回退"""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "system" / "Win-Service-Optimizer" / "win_service_optimizer.py"


def load_module():
    if "tkinter" not in sys.modules:
        try:
            import tkinter  # noqa: F401
            import tkinter.messagebox  # noqa: F401
            import tkinter.ttk  # noqa: F401
        except ImportError:
            tk = types.ModuleType("tkinter")
            tk.Tk = object
            tk.messagebox = types.ModuleType("tkinter.messagebox")
            tk.ttk = types.ModuleType("tkinter.ttk")
            sys.modules.update({
                "tkinter": tk,
                "tkinter.messagebox": tk.messagebox,
                "tkinter.ttk": tk.ttk,
            })
    tk = sys.modules["tkinter"]
    if not hasattr(tk, "Tk"):
        tk.Tk = object
    if "tkinter.ttk" not in sys.modules:
        ttk = getattr(tk, "ttk", types.ModuleType("tkinter.ttk"))
        tk.ttk = ttk
        sys.modules["tkinter.ttk"] = ttk
    if "tkinter.messagebox" not in sys.modules:
        mb = getattr(tk, "messagebox", types.ModuleType("tkinter.messagebox"))
        tk.messagebox = mb
        sys.modules["tkinter.messagebox"] = mb
    spec = importlib.util.spec_from_file_location("win_service_optimizer_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class WinServiceOptimizerTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_decode_output_handles_utf8_and_gbk(self):
        self.assertEqual(self.mod._decode_output(b""), "")
        self.assertEqual(self.mod._decode_output("服务已停止".encode("utf-8")), "服务已停止")
        with mock.patch.object(self.mod.os, "name", "nt"):
            self.assertEqual(
                self.mod._decode_output("拒绝访问。".encode("gbk")),
                "拒绝访问。",
            )

    def test_set_service_uses_separate_start_argument(self):
        calls = []

        def fake_run_sc(*args):
            calls.append(args)
            return 0, ""

        with mock.patch.object(self.mod, "run_sc", side_effect=fake_run_sc):
            res = self.mod.set_service("DiagTrack", "disabled")
        self.assertEqual(calls[0], ("config", "DiagTrack", "start=", "disabled"))
        self.assertEqual(calls[1], ("stop", "DiagTrack"))
        self.assertIn("已设为“禁用”", res)

    def test_set_service_falls_back_to_registry_on_access_denied(self):
        with mock.patch.object(self.mod, "is_admin", return_value=True), \
                mock.patch.object(self.mod, "run_sc", side_effect=[(5, "拒绝访问"), (5, "拒绝访问")]), \
                mock.patch.object(self.mod, "_set_start_in_registry") as reg_fn:
            res = self.mod.set_service("DoSvc", "disabled")
        reg_fn.assert_called_once_with("DoSvc", "disabled")
        self.assertIn("已通过注册表设为“禁用”", res)
        self.assertIn("重启电脑后生效", res)

    def test_set_service_non_admin_does_not_touch_registry(self):
        with mock.patch.object(self.mod, "is_admin", return_value=False), \
                mock.patch.object(self.mod, "run_sc", return_value=(5, "拒绝访问")), \
                mock.patch.object(self.mod, "_set_start_in_registry") as reg_fn:
            res = self.mod.set_service("DoSvc", "disabled")
        reg_fn.assert_not_called()
        self.assertTrue(res.startswith("❌"))

    def test_set_service_reports_registry_error(self):
        with mock.patch.object(self.mod, "is_admin", return_value=True), \
                mock.patch.object(self.mod, "run_sc", return_value=(5, "拒绝访问")), \
                mock.patch.object(self.mod, "_set_start_in_registry", side_effect=PermissionError("denied")):
            res = self.mod.set_service("DoSvc", "auto")
        self.assertIn("注册表写入也失败", res)
        self.assertTrue(res.startswith("❌"))

    def test_set_start_in_registry_writes_reg_dword(self):
        fake_winreg = types.SimpleNamespace(
            HKEY_LOCAL_MACHINE="HKLM",
            KEY_SET_VALUE=2,
            REG_DWORD=4,
            OpenKey=mock.MagicMock(return_value="HANDLE"),
            SetValueEx=mock.MagicMock(),
            CloseKey=mock.MagicMock(),
        )
        with mock.patch.object(self.mod.os, "name", "nt"), \
                mock.patch.dict(sys.modules, {"winreg": fake_winreg}):
            self.mod._set_start_in_registry("DoSvc", "disabled")
        fake_winreg.OpenKey.assert_called_once_with(
            "HKLM", r"SYSTEM\CurrentControlSet\Services\DoSvc", 0, 2
        )
        fake_winreg.SetValueEx.assert_called_once_with("HANDLE", "Start", 0, 4, 4)
        fake_winreg.CloseKey.assert_called_once_with("HANDLE")


if __name__ == "__main__":
    unittest.main()
