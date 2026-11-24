"""Article cards beside the CAD/Revit and Green Belt products.

Same shape as the Lighting Controls article: Medium title link, Medium
primary button, Substack secondary button.

Run from the repo root: python3 -m unittest tests/test_shop_articles.py
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

AI_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "ai-in-autocad-and-revit-in-2026-what-it-actually-does-for-drafters-c3c1e17707ad"
)
AI_SUBSTACK = "https://robinwolfson.substack.com/p/ai-in-autocad-and-revit-in-2026-what"
AI_TITLE = (
    "AI in AutoCAD and Revit in 2026: What It Actually Does (and Where It Still Fumbles)"
)
GB_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "asq-vs-iassc-vs-cssc-which-green-belt-certification-should-you-actually-take-8d0041754f11"
)
GB_SUBSTACK = "https://robinwolfson.substack.com/p/asq-vs-iassc-vs-cssc-which-green"
GB_TITLE = "ASQ vs IASSC vs CSSC: Which Green Belt Certification Should You Actually Take?"
BANNED_CHECKOUTS = ("/e/593903", "/e/593901", "/e/593132")


def articles(html):
    return re.findall(r"<article\b([^>]*)>(.*?)</article>", html, flags=re.S)


def attr(attrs, name):
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else ""


def plain(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    text = text.replace("&amp;", "&").replace("&middot;", "·")
    return re.sub(r"\s+", " ", text).strip()


def text_of(fragment, tag):
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", fragment, flags=re.S)
    return plain(match.group(1)) if match else ""


def hrefs(fragment, class_name):
    return re.findall(rf'<a class="{class_name}" href="([^"]+)"([^>]*)>', fragment)


class ShopArticleCardsTest(unittest.TestCase):
    def setUp(self):
        self.cards = {attr(attrs, "id"): body for attrs, body in articles(HTML)}
        self.products = HTML.split('id="products"', 1)[1].split('id="extras"', 1)[0]
        self.lean = self.products.split('id="lean-six-sigma"', 1)[1].split('id="cad"', 1)[0]
        self.cad = self.products.split('id="cad"', 1)[1].split('id="revit"', 1)[0]

    def assert_article(self, card, title, medium, substack):
        self.assertEqual(text_of(card, "h3"), title)
        self.assertIn("Article on Medium and Substack", card)
        self.assertIn(">Article<", card)
        self.assertIn(">Medium &amp; Substack<", card)
        self.assertNotIn('class="price"', card)
        self.assertNotIn("buymeacoffee.com", card)
        self.assertNotIn("<img", card)
        primary = hrefs(card, "btn btn-primary")
        secondary = hrefs(card, "btn btn-secondary")
        title_link = hrefs(card, "card-title-link")
        self.assertEqual([href for href, _ in primary], [medium])
        self.assertEqual([href for href, _ in secondary], [substack])
        self.assertEqual([href for href, _ in title_link], [medium])
        self.assertIn("Read on Medium", card)
        self.assertIn("Read on Substack", card)
        for _, extra in primary + secondary + title_link:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)

    def test_ai_article_sits_with_the_cad_products(self):
        card = self.cards["ai-autocad-revit-article"]
        self.assertIn(card, self.cad)
        self.assertLess(self.cad.index('id="ai-prompt-pack"'), self.cad.index('id="ai-autocad-revit-article"'))
        self.assertLess(
            self.products.index('id="ai-autocad-revit-article"'),
            self.products.index('id="revit"'),
        )
        self.assertNotIn('id="ai-autocad-revit-article"', self.lean)
        self.assert_article(card, AI_TITLE, AI_MEDIUM, AI_SUBSTACK)
        self.assertIn(">AutoCAD and Revit<", card)
        self.assertIn("#ai-autocad-revit-article .purchase-actions,", CSS)

    def test_green_belt_article_sits_with_the_study_products(self):
        card = self.cards["green-belt-certification-article"]
        self.assertIn(card, self.lean)
        self.assertLess(
            self.lean.index("The Lean Six Sigma Toolkit"),
            self.lean.index('id="green-belt-certification-article"'),
        )
        self.assertLess(
            self.products.index('id="green-belt-certification-article"'),
            self.products.index('id="cad"'),
        )
        self.assertNotIn('id="green-belt-certification-article"', self.cad)
        self.assert_article(card, GB_TITLE, GB_MEDIUM, GB_SUBSTACK)
        self.assertIn(">Green Belt certification<", card)
        self.assertIn("#green-belt-certification-article .purchase-actions { flex-direction: column; }", CSS)
        self.assertIn("#green-belt-certification-article { align-self: start; }", CSS)

    def test_banned_checkouts_stay_off_the_page(self):
        for path in BANNED_CHECKOUTS:
            self.assertNotIn(path, HTML)
