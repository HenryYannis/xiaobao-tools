"""依赖声明：代码里 import 的第三方库都要写进根目录 requirements.txt"""
import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "scratch-assets", "tests"}

# import 名 -> PyPI 包名
DIST_NAMES = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "win32api": "pywin32",
    "win32event": "pywin32",
    "winerror": "pywin32",
    "win32con": "pywin32",
    "win32gui": "pywin32",
}


def source_files():
    for path in ROOT.rglob("*.py*"):
        if path.suffix in (".py", ".pyw") and not SKIP_DIRS & set(path.relative_to(ROOT).parts):
            yield path


def third_party_imports():
    found = {}
    for path in source_files():
        local = {p.stem for p in path.parent.glob("*.py")}
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top in sys.stdlib_module_names or top in local or top in ("winreg", "msvcrt", "_winapi"):
                    continue
                found.setdefault(top, path.relative_to(ROOT).as_posix())
    return found


def declared(req_file):
    names = set()
    for line in (ROOT / req_file).read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            names.add(re.split(r"[<>=!~;\[ ]", line, 1)[0].lower())
    return names


@unittest.skipUnless(hasattr(sys, "stdlib_module_names"), "需要 Python 3.10+")
class RequirementsTest(unittest.TestCase):
    def test_all_third_party_imports_declared(self):
        req = declared("requirements.txt")
        missing = {
            mod: where for mod, where in third_party_imports().items()
            if DIST_NAMES.get(mod, mod).lower() not in req
        }
        self.assertEqual(missing, {}, "这些库在代码里用到了，但 requirements.txt 里没有")

    def test_productivity_matches_root(self):
        self.assertLessEqual(declared("productivity/requirements.txt"), declared("requirements.txt"))
        self.assertIn("opencv-python", declared("productivity/requirements.txt"))

    def test_system_declares_pywin32(self):
        self.assertIn("pywin32", declared("system/requirements.txt"))

    def test_pypi_txt_has_no_unused_pygame(self):
        for path in ROOT.rglob("PyPI.txt"):
            self.assertNotIn("pygame", path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
