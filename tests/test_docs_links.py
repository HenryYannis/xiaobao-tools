"""文档：README / CHANGELOG 里的本地相对链接都要指向真实存在的文件或目录"""
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["README.md", "README_EN.md", "CHANGELOG.md", "network/LAN-AI-Chat/README.md"]
LINK = re.compile(r"\]\(([^)\s]+)\)")


def local_links(doc):
    text = (ROOT / doc).read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue  # 外部链接和页内锚点不检查
        yield unquote(target.split("#")[0])


class DocsLinksTest(unittest.TestCase):
    def test_local_links_exist(self):
        broken = []
        for doc in DOCS:
            base = (ROOT / doc).parent
            for target in local_links(doc):
                if not (base / target).exists():
                    broken.append(f"{doc}: {target}")
        self.assertEqual(broken, [], "这些链接指向的文件不存在")

    def test_every_tool_folder_listed_in_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        missing = [
            f"{group}/{folder.name}"
            for group in ("network", "system", "productivity", "favorites")
            for folder in sorted((ROOT / group).iterdir())
            if folder.is_dir() and f"./{group}/{folder.name}" not in readme
        ]
        self.assertEqual(missing, [], "README 没有列出这些工具目录")


if __name__ == "__main__":
    unittest.main()
