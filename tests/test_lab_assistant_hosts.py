"""机房助手：修改 hosts 时先备份、整体替换，保持原有编码"""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "system" / "lab-assistant" / "lab_assistant.py"

WINREG_NAMES = ("HKEY_CLASSES_ROOT HKEY_CURRENT_USER HKEY_LOCAL_MACHINE HKEY_USERS OpenKey CreateKey CreateKeyEx "
                "SetValueEx DeleteValue DeleteKey DeleteKeyEx EnumKey EnumValue QueryValueEx QueryInfoKey CloseKey "
                "REG_DWORD REG_SZ REG_EXPAND_SZ KEY_READ KEY_WRITE KEY_ALL_ACCESS KEY_WOW64_64KEY")


def load_module():
    if "tkinter" not in sys.modules:
        tk = types.ModuleType("tkinter")
        tk.messagebox = types.ModuleType("tkinter.messagebox")
        tk.filedialog = types.ModuleType("tkinter.filedialog")
        sys.modules.update({"tkinter": tk, "tkinter.messagebox": tk.messagebox, "tkinter.filedialog": tk.filedialog})
    if "winreg" not in sys.modules:
        fake = types.ModuleType("winreg")
        for name in WINREG_NAMES.split():
            setattr(fake, name, 0)
        sys.modules["winreg"] = fake
    spec = importlib.util.spec_from_file_location("lab_assistant_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HostsWriteTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.dir = tempfile.mkdtemp()
        self.hosts = os.path.join(self.dir, "hosts")
        self.mod.SYSTEM_HOSTS_PATH = self.hosts
        self.mod.SYSTEM_HOSTS_BACKUP = self.hosts + ".xiaobao.bak"

    def test_backup_once_and_replace(self):
        Path(self.hosts).write_bytes(b"127.0.0.1 localhost\r\n")
        text = self.mod._read_system_hosts()
        self.assertTrue(self.mod._write_system_hosts(text + "1.2.3.4 a.com\r\n"))
        self.assertTrue(self.mod._write_system_hosts("changed again\r\n"))
        self.assertEqual(Path(self.mod.SYSTEM_HOSTS_BACKUP).read_bytes(), b"127.0.0.1 localhost\r\n")
        self.assertEqual(Path(self.hosts).read_bytes(), b"changed again\r\n")
        self.assertFalse(os.path.exists(self.hosts + ".xiaobao.tmp"))

    def test_failure_keeps_original(self):
        Path(self.hosts).write_bytes(b"127.0.0.1 localhost\n")
        with mock.patch.object(self.mod.os, "replace", side_effect=OSError("disk error")):
            self.assertFalse(self.mod._write_system_hosts("broken"))
        self.assertEqual(Path(self.hosts).read_bytes(), b"127.0.0.1 localhost\n")
        self.assertFalse(os.path.exists(self.hosts + ".xiaobao.tmp"))

    def test_keeps_gbk_encoding(self):
        original = "# 中文注释\n127.0.0.1 localhost\n".encode("gbk")
        Path(self.hosts).write_bytes(original)
        text = self.mod._read_system_hosts()
        self.assertIn("中文注释", text)
        self.assertTrue(self.mod._write_system_hosts(text + "1.2.3.4 a.com\n"))
        self.assertTrue(Path(self.hosts).read_bytes().startswith(original))


if __name__ == "__main__":
    unittest.main()
