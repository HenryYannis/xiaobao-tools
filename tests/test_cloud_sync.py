"""云端白名单同步：内嵌脚本与 Sync-Whitelist.ps1 一致；拉到网页或格式不对的内容时整份丢弃"""
import ast
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "favorites" / "one-assistant"
PS1 = APP / "Sync-Whitelist.ps1"


def embedded_script():
    tree = ast.parse((APP / "config.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SYNC_SCRIPT_CONTENT":
            return node.value.value
    raise AssertionError("config.py 里没有 SYNC_SCRIPT_CONTENT")


class CloudSyncScriptTest(unittest.TestCase):
    def test_embedded_copy_matches_file(self):
        self.assertEqual(embedded_script(), PS1.read_text(encoding="utf-8-sig"),
                         "改了 Sync-Whitelist.ps1 后要同步更新 config.py 里的 SYNC_SCRIPT_CONTENT")

    @unittest.skipUnless(shutil.which("pwsh"), "需要 PowerShell 7 (pwsh)")
    def test_validation_rejects_html_and_garbage(self):
        text = PS1.read_text(encoding="utf-8")
        start = text.index("$SyncLog =")
        end = text.index("$rules = $null")
        tmp = tempfile.mkdtemp()
        log_path = r"C:\ProgramData\XiaobaoTools\sync.log"
        funcs = text[start:end].replace(log_path, tmp + "/sync.log")
        good = (APP / "whitelist.txt").read_text(encoding="utf-8").replace("'", "''")
        script = f"""
$CacheDir = '{tmp}'
{funcs}
$r = Get-ValidRules '{good}' 'good';  if ($r) {{ "good=$($r.Count)" }} else {{ 'good=null' }}
$r = Get-ValidRules '<html><body>login</body></html>' 'html'; if ($r) {{ 'html=ok' }} else {{ 'html=null' }}
$r = Get-ValidRules "a.com`nevil site.com" 'space'; if ($r) {{ 'space=ok' }} else {{ 'space=null' }}
$r = Get-ValidRules "# only comments" 'empty'; if ($r) {{ 'empty=ok' }} else {{ 'empty=null' }}
"""
        out = subprocess.run(["pwsh", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        lines = out.stdout.split()
        good_count = sum(1 for line in (APP / "whitelist.txt").read_text(encoding="utf-8").splitlines()
                         if line.strip() and not line.strip().startswith("#"))
        self.assertIn(f"good={good_count}", lines)
        self.assertIn("html=null", lines)
        self.assertIn("space=null", lines)
        self.assertIn("empty=null", lines)


if __name__ == "__main__":
    unittest.main()
