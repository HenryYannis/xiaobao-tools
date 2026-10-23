"""一体化助手：重启浏览器时不能再用 shell=True 套两层 cmd"""
import ast
import subprocess
import unittest
from pathlib import Path
from unittest import mock

UI_PY = Path(__file__).resolve().parents[1] / "favorites" / "one-assistant" / "ui.py"


def load_launch_browser():
    # ui.py 顶层依赖 tkinter 和 winreg，这里只取出 launch_browser 这一个函数来测
    tree = ast.parse(UI_PY.read_text(encoding="utf-8"))
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "launch_browser")
    ns = {"subprocess": subprocess}
    exec(compile(ast.Module(body=[func], type_ignores=[]), str(UI_PY), "exec"), ns)
    return ns["launch_browser"]


class LaunchBrowserTest(unittest.TestCase):
    def call(self, *args):
        launch_browser = load_launch_browser()
        with mock.patch.object(subprocess, "Popen") as popen:
            launch_browser(*args)
        self.assertEqual(popen.call_count, 1)
        return popen.call_args

    def test_no_shell_and_empty_title(self):
        call = self.call("msedge")
        self.assertNotIn("shell", call.kwargs)
        self.assertEqual(call.args[0], 'cmd /c start "" "msedge"')

    def test_url_is_quoted(self):
        call = self.call("chrome", "https://example.com/a?x=1&y=2")
        self.assertEqual(call.args[0], 'cmd /c start "" "chrome" "https://example.com/a?x=1&y=2"')

    def test_no_shell_true_left_in_ui(self):
        self.assertNotIn("shell=True)", UI_PY.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
