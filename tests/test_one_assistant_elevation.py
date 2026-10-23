"""一体化助手：从源码运行时，提权后重新启动的必须是入口程序"""
import ctypes
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "favorites" / "one-assistant"


def load_reg_utils():
    # 非 Windows 环境用空的 winreg 代替，只测试提权参数
    if "winreg" not in sys.modules:
        fake = types.ModuleType("winreg")
        for name in ("HKEY_CLASSES_ROOT HKEY_CURRENT_USER HKEY_LOCAL_MACHINE OpenKey CreateKey SetValueEx "
                     "DeleteValue DeleteKey EnumKey QueryValueEx QueryInfoKey REG_DWORD REG_SZ KEY_READ KEY_ALL_ACCESS").split():
            setattr(fake, name, None)
        sys.modules["winreg"] = fake
    spec = importlib.util.spec_from_file_location("reg_utils_under_test", APP_DIR / "reg_utils.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ElevationTest(unittest.TestCase):
    def run_elevation(self, argv, frozen=False):
        mod = load_reg_utils()
        calls = []
        shell32 = types.SimpleNamespace(ShellExecuteW=lambda *a: calls.append(a) or 42)
        windll = types.SimpleNamespace(shell32=shell32)
        with mock.patch.object(ctypes, "windll", windll, create=True), \
                mock.patch.object(sys, "argv", argv), \
                mock.patch.object(sys, "frozen", frozen, create=True):
            with self.assertRaises(SystemExit) as cm:
                mod.run_as_admin()
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(len(calls), 1)
        return calls[0]

    def test_source_run_relaunches_entry_script(self):
        entry = str(APP_DIR / "one_assistant.py")
        _, verb, exe, params, workdir, _ = self.run_elevation([entry])
        self.assertEqual(verb, "runas")
        self.assertEqual(exe, sys.executable)
        self.assertIn("one_assistant.py", params)
        self.assertNotIn("reg_utils.py", params)
        self.assertTrue(params.endswith("--elevated"))
        self.assertEqual(Path(workdir), APP_DIR)

    def test_frozen_run_passes_only_flag(self):
        _, _, exe, params, _, _ = self.run_elevation(["one_assistant.exe"], frozen=True)
        self.assertEqual(exe, sys.executable)
        self.assertEqual(params, "--elevated")


if __name__ == "__main__":
    unittest.main()
