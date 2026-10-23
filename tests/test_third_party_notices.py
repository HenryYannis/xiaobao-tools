"""第三方声明：内嵌的 QRCode 库和 Scratch 素材要有署名和许可证说明"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ThirdPartyNoticesTest(unittest.TestCase):
    def setUp(self):
        self.notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")

    def test_qrcode_attribution(self):
        self.assertIn("davidshimjs/qrcodejs", self.notices)
        self.assertIn("Copyright (c) 2012 davidshimjs", self.notices)
        self.assertIn("Kazuhiko Arase", self.notices)
        html = (ROOT / "productivity" / "Bitwarden-Vault-Cleaner" / "index.html").read_text(encoding="utf-8")
        self.assertIn("var QRCode;", html)
        self.assertIn("davidshimjs", html)

    def test_scratch_assets_attribution(self):
        self.assertIn("scratch-assets/", self.notices)
        self.assertIn("Scratch Foundation", self.notices)
        self.assertIn("CC BY-SA", self.notices)


if __name__ == "__main__":
    unittest.main()
