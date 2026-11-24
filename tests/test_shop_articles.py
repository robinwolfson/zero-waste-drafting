"""Articles section: every published article, newest first.

Four pieces are on Medium and Substack. The two oldest are on Medium only;
their Substack URLs do not exist, so those cards do not invent a Substack link.

Run from the repo root: python3 -m unittest tests/test_shop_articles.py
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "learn.html").read_text(encoding="utf-8")
SHOP = (ROOT / "shop.html").read_text(encoding="utf-8")
FREE = (ROOT / "free.html").read_text(encoding="utf-8")
HOME = (ROOT / "index.html").read_text(encoding="utf-8")
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
FL_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "dont-copy-a-2021-iecc-lighting-controls-cheat-sheet-onto-a-florida-permit-set-bfe1dcf85039"
)
FL_SUBSTACK = "https://robinwolfson.substack.com/p/dont-copy-a-2021-iecc-lighting-controls"
FL_TITLE = "Don\u2019t Copy a 2021 IECC Lighting-Controls Cheat Sheet onto a Florida Permit Set"
CAD_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "how-to-set-up-autocad-drawing-standards-as-a-freelancer-or-small-firm-2e800366d722"
)
CAD_SUBSTACK = "https://robinwolfson.substack.com/p/how-to-set-up-autocad-drawing-standards"
CAD_TITLE = "How to Set Up AutoCAD Drawing Standards as a Freelancer or Small Firm"
REVIT_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "revit-naming-standards-for-small-firms-views-sheets-families-and-files-f4ad03afa216"
)
REVIT_TITLE = "Revit Naming Standards for Small Firms: Views, Sheets, Families, and Files"
EXAM_MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "how-to-pass-the-lean-six-sigma-green-belt-exam-without-a-500-page-textbook-7b997f7facf3"
)
EXAM_TITLE = "How to Pass the Lean Six Sigma Green Belt Exam Without a 500-Page Textbook"
BANNED_CHECKOUTS = ("/e/593903", "/e/593901", "/e/593132")

# Newest first. substack is None when Robin has not published that piece there.
PUBLISHED = (
    ("green-belt-certification-article", GB_TITLE, "Green Belt certification", GB_MEDIUM, GB_SUBSTACK),
    ("ai-autocad-revit-article", AI_TITLE, "AutoCAD and Revit", AI_MEDIUM, AI_SUBSTACK),
    ("florida-lighting-article", FL_TITLE, "Florida permit sets", FL_MEDIUM, FL_SUBSTACK),
    ("autocad-standards-article", CAD_TITLE, "AutoCAD standards", CAD_MEDIUM, CAD_SUBSTACK),
    ("revit-naming-article", REVIT_TITLE, "Revit naming", REVIT_MEDIUM, None),
    ("green-belt-exam-article", EXAM_TITLE, "Green Belt exam", EXAM_MEDIUM, None),
)


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


class ArticlesSectionTest(unittest.TestCase):
    def setUp(self):
        self.section = HTML.split('id="articles"', 1)[1].split('id="videos"', 1)[0]
        self.cards = [(attr(attrs, "id"), body) for attrs, body in articles(self.section)]
        self.by_id = {card_id: body for card_id, body in self.cards}

    def test_section_sits_in_the_nav_after_lighting_controls(self):
        self.assertLess(HTML.index('id="articles"'), HTML.index('id="videos"'))
        self.assertLess(HTML.index('id="videos"'), HTML.index('id="lighting-shorts"'))
        self.assertIn('id="free-quiz"', FREE)
        self.assertIn('id="faq"', HOME)
        self.assertLess(SHOP.index('id="lighting-controls"'), SHOP.index("<footer"))
        self.assertEqual(text_of(self.section, "h2"), "Articles")
        self.assertIn(
            "Field notes on Lean Six Sigma, commercial CAD and Revit, and Florida lighting controls.",
            self.section,
        )
        header = HTML.split('aria-label="Main"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(
            re.findall(r'href="([^"]+)"', header),
            ["index.html", "shop.html", "free.html", "learn.html"],
        )
        self.assertIn('class="grid"', self.section)
        self.assertIn("#articles,\n#videos,", CSS)
        self.assertIn(".article-card .purchase-actions { flex-direction: column; }", CSS)
        self.assertIn("grid-template-columns: repeat(2, 1fr)", CSS)
        self.assertIn(".grid > .card { grid-column: span 2; }", CSS)

    def test_cards_are_newest_first_and_not_duplicated(self):
        self.assertEqual([card_id for card_id, _ in self.cards], [row[0] for row in PUBLISHED])
        for card_id, title, topic, medium, substack in PUBLISHED:
            self.assertEqual(HTML.count(f'id="{card_id}"'), 1, card_id)
            card = self.by_id[card_id]
            self.assertEqual(text_of(card, "h3"), title)
            self.assertIn(">Article<", card)
            self.assertIn(f">{topic}<", card)
            self.assertNotIn('class="price"', card)
            self.assertNotIn("buymeacoffee.com", card)
            self.assertNotIn("<img", card)
            self.assertIn('class="license-banner"', card)
            primary = hrefs(card, "btn btn-primary")
            title_link = hrefs(card, "card-title-link")
            self.assertEqual([href for href, _ in primary], [medium])
            self.assertEqual([href for href, _ in title_link], [medium])
            self.assertIn("Read on Medium", card)
            if substack:
                secondary = hrefs(card, "btn btn-secondary")
                self.assertEqual([href for href, _ in secondary], [substack])
                self.assertIn(">Medium &amp; Substack<", card)
                self.assertIn("Article on Medium and Substack", card)
                self.assertIn("Read on Substack", card)
                linked = primary + secondary + title_link
            else:
                self.assertNotIn("substack.com", card)
                self.assertNotIn("btn-secondary", card)
                self.assertIn(">Medium<", card)
                self.assertIn(">Article on Medium<", card)
                self.assertNotIn("Read on Substack", card)
                linked = primary + title_link
            for _, extra in linked:
                self.assertIn('target="_blank"', extra)
                self.assertIn('rel="noopener"', extra)

    def test_product_sections_keep_a_text_link_instead_of_the_card(self):
        lean = SHOP.split('id="lean-six-sigma"', 1)[1].split('id="cad"', 1)[0]
        cad = SHOP.split('id="cad"', 1)[1].split('id="revit"', 1)[0]
        lighting = SHOP.split('id="lighting-controls"', 1)[1].split("<footer", 1)[0]
        self.assertNotIn('id="green-belt-certification-article"', lean)
        self.assertNotIn('id="ai-autocad-revit-article"', cad)
        self.assertNotIn('id="florida-lighting-article"', lighting)
        self.assertIn('href="learn.html#green-belt-certification-article"', lean)
        self.assertIn('href="learn.html#ai-autocad-revit-article"', cad)
        self.assertIn('href="learn.html#florida-lighting-article"', lighting)
        for fragment in (lean, cad, lighting):
            self.assertEqual(fragment.count(">Read the related article<"), 1)
            self.assertIn('class="related-reading"', fragment)

    def test_banned_checkouts_stay_off_the_page(self):
        for path in BANNED_CHECKOUTS:
            for page in (HTML, SHOP, FREE, HOME):
                self.assertNotIn(path, page)
