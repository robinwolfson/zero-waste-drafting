"""AI Prompt Pack card in the CAD and Revit shop.

Run from the repo root: python3 -m unittest tests/test_ai_prompt_pack.py
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "shop.html").read_text(encoding="utf-8")

BMAC = "https://buymeacoffee.com/robinwolfson/e/599857"
ETSY = "https://www.etsy.com/listing/4620552083/ai-prompt-pack-for-cad-and-revit"
TITLE = "AI Prompt Pack for CAD and Revit Drafters"
DESCRIPTION = (
    "40 practical AI prompts for CAD and Revit work: Revit naming audits, "
    "first-pass plan notes, AutoCAD layer cleanup, sheet index and title-block text, "
    "RFIs and submittals, QA/QC checklists, Dynamo and AutoLISP starters, "
    "spec summaries and Lean drafting improvement. Every prompt includes an example "
    "and a check you still do."
)
DISCLAIMER = "AI output is a first draft, not code-compliant on its own."


def articles(html):
    return re.findall(r"<article\b([^>]*)>(.*?)</article>", html, flags=re.S)


def attr(attrs, name):
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else ""


def plain(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    text = (
        text.replace("&amp;", "&")
        .replace("&middot;", "·")
        .replace("&mdash;", "—")
    )
    return re.sub(r"\s+", " ", text).strip()


def text_of(fragment, tag):
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", fragment, flags=re.S)
    return plain(match.group(1)) if match else ""


def hrefs(fragment, class_name):
    return re.findall(rf'<a class="{class_name}" href="([^"]+)"([^>]*)>', fragment)


class AiPromptPackCardTest(unittest.TestCase):
    def setUp(self):
        found = [body for attrs, body in articles(HTML) if attr(attrs, "id") == "ai-prompt-pack"]
        self.assertEqual(len(found), 1)
        self.card = found[0]
        self.products = HTML.split('id="products"', 1)[1].split('id="extras"', 1)[0]
        self.cad = self.products.split('id="cad"', 1)[1].split('id="revit"', 1)[0]

    def test_card_sits_with_the_cad_and_revit_products(self):
        self.assertIn(self.card, self.cad)
        self.assertLess(self.cad.index('id="autocad-standards-pack"'), self.cad.index('id="ai-prompt-pack"'))
        self.assertLess(self.products.index('id="ai-prompt-pack"'), self.products.index('id="revit"'))
        extras = HTML.split('id="extras"', 1)[1].split('id="preview"', 1)[0]
        lighting = HTML.split('id="lighting-controls"', 1)[1].split('id="free-quiz"', 1)[0]
        self.assertNotIn('id="ai-prompt-pack"', extras)
        self.assertNotIn('id="ai-prompt-pack"', lighting)
        self.assertNotIn("<img", self.card)
        self.assertNotIn("http://", self.card)
        self.assertNotIn("https://", self.card.split('href="https://buymeacoffee.com', 1)[0])

    def test_copy_format_and_disclaimer(self):
        self.assertEqual(text_of(self.card, "h3"), TITLE)
        self.assertIn("PDF + editable text, 24 pages", self.card)
        self.assertIn(DESCRIPTION, plain(self.card))
        self.assertIn(DISCLAIMER, plain(self.card))
        self.assertIn('class="note"', self.card)
        self.assertIn("$12", self.card)
        self.assertIn("Etsy $14", self.card)

    def test_store_buttons(self):
        primary = hrefs(self.card, "btn btn-primary")
        secondary = hrefs(self.card, "btn btn-secondary")
        title = hrefs(self.card, "card-title-link")
        self.assertEqual([href for href, _ in primary], [BMAC])
        self.assertEqual([href for href, _ in secondary], [ETSY])
        self.assertEqual([href for href, _ in title], [BMAC])
        self.assertIn(">Buy on Buy Me a Coffee — $12<", self.card)
        self.assertIn(">Etsy — $14<", self.card)
        for _, extra in primary + secondary + title:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)
        self.assertIn('class="purchase-actions"', self.card)

    def test_social_links_stay(self):
        self.assertIn('content="@RobinCWolfson"', HTML)
        self.assertIn('href="https://x.com/RobinCWolfson"', HTML)
        self.assertIn('href="https://www.youtube.com/@ZeroWasteDrafting"', HTML)
        self.assertIn("X (@RobinCWolfson)", HTML)


if __name__ == "__main__":
    unittest.main()
