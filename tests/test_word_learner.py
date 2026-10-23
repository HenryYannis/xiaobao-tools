"""单词联机学习器：从别的目录运行时也要读到 words.txt"""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "productivity" / "LAN-Word-Learner" / "word_learner.py"


def load_module():
    if "tkinter" not in sys.modules:
        tk = types.ModuleType("tkinter")
        tk.messagebox = types.ModuleType("tkinter.messagebox")
        sys.modules.update({"tkinter": tk, "tkinter.messagebox": tk.messagebox})
    spec = importlib.util.spec_from_file_location("word_learner_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class WordLearnerTest(unittest.TestCase):
    def test_loads_word_file_from_other_cwd(self):
        old = os.getcwd()
        os.chdir(tempfile.mkdtemp())  # 模拟在仓库根目录或其他目录运行
        try:
            mod = load_module()
        finally:
            os.chdir(old)
        self.assertGreater(len(mod.WORDS), 100)
        self.assertIn(("一个", "a"), mod.WORDS)

    def test_local_ip_is_valid(self):
        mod = load_module()
        parts = mod.HOST_IP.split(".")
        self.assertEqual(len(parts), 4)


if __name__ == "__main__":
    unittest.main()
