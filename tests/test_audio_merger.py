"""音频合并：不再全局改 subprocess.Popen，ffmpeg 先找 PATH 再找脚本目录"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "productivity" / "Audio-Merger" / "audio_merger.py"


def stub_modules():
    # CI 里不一定有 tkinter 和 pydub，用空模块代替，只测查找逻辑
    tk = types.ModuleType("tkinter")
    for name in ("filedialog", "messagebox", "ttk"):
        sub = types.ModuleType("tkinter." + name)
        setattr(tk, name, sub)
    pydub = types.ModuleType("pydub")
    pydub.AudioSegment = type("AudioSegment", (), {})
    seg = types.ModuleType("pydub.audio_segment")
    seg.subprocess = subprocess
    utils = types.ModuleType("pydub.utils")
    utils.Popen = subprocess.Popen
    pydub.audio_segment, pydub.utils = seg, utils
    return {
        "tkinter": tk, "tkinter.filedialog": tk.filedialog, "tkinter.messagebox": tk.messagebox,
        "tkinter.ttk": tk.ttk, "pydub": pydub, "pydub.audio_segment": seg, "pydub.utils": utils,
    }


def load(which=lambda name: None, platform=None):
    with mock.patch.dict(sys.modules, stub_modules()), \
            mock.patch("shutil.which", which), \
            mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", "")}), \
            mock.patch.object(sys, "platform", platform or sys.platform):
        spec = importlib.util.spec_from_file_location("audio_merger_under_test", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, sys.modules["pydub.audio_segment"], sys.modules["pydub.utils"]


class AudioMergerTest(unittest.TestCase):
    def test_global_popen_untouched(self):
        original = subprocess.Popen
        load(which=lambda n: "/usr/bin/" + n, platform="win32")
        self.assertIs(subprocess.Popen, original)

    def test_windows_only_pydub_gets_hidden_popen(self):
        mod, seg, utils = load(which=lambda n: "/usr/bin/" + n, platform="win32")
        self.assertIs(utils.Popen, mod._hidden_popen)
        self.assertIs(seg.subprocess.Popen, mod._hidden_popen)
        self.assertIs(seg.subprocess.PIPE, subprocess.PIPE)

    def test_prefers_path(self):
        mod, _, _ = load(which=lambda n: "/usr/bin/" + n)
        self.assertEqual(mod.ffmpeg_exe, "/usr/bin/ffmpeg")
        self.assertEqual(mod.ffprobe_exe, "/usr/bin/ffprobe")
        self.assertIsNone(mod.check_environment())

    def test_falls_back_to_script_dir(self):
        mod, _, _ = load()
        with tempfile.TemporaryDirectory() as d:
            Path(d, "ffmpeg.exe").write_bytes(b"")
            with mock.patch("shutil.which", lambda n: None):
                self.assertEqual(mod.find_tool("ffmpeg", d), os.path.join(d, "ffmpeg.exe"))
                self.assertIsNone(mod.find_tool("ffprobe", d))

    def test_missing_ffmpeg_gives_download_hint(self):
        mod, _, _ = load()
        if mod.ffmpeg_exe and mod.ffprobe_exe:
            self.skipTest("脚本目录里放了 ffmpeg")
        problem = mod.check_environment()
        self.assertIn("ffmpeg", problem)
        self.assertIn(mod.FFMPEG_DOWNLOAD_URL, problem)
        ok, msg = mod.merge_mp3_files(tempfile.gettempdir(), "out.mp3")
        self.assertFalse(ok)
        self.assertEqual(msg, problem)


if __name__ == "__main__":
    unittest.main()
