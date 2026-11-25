"""Lighting Controls section: Florida shorts, article, and permit kit.

Run from the repo root: python3 -m unittest tests/test_lighting_controls.py
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
LEARN = HTML
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

MEDIUM = (
    "https://medium.com/@robinwolfson.drafting/"
    "dont-copy-a-2021-iecc-lighting-controls-cheat-sheet-onto-a-florida-permit-set-bfe1dcf85039"
)
SUBSTACK = "https://robinwolfson.substack.com/p/dont-copy-a-2021-iecc-lighting-controls"
BMAC = "https://buymeacoffee.com/robinwolfson/e/595488"
ETSY = "https://www.etsy.com/listing/4611461235"
YOUTUBE = "https://www.youtube.com/@ZeroWasteDrafting"
ARTICLE = "Don\u2019t Copy a 2021 IECC Lighting-Controls Cheat Sheet onto a Florida Permit Set"
DISCLAIMER = (
    "Educational summary, not a substitute for the adopted Florida Energy Conservation Code or your AHJ."
)
EPISODE_LINE = '<li><a href="https://www.youtube.com/shorts/VIDEO_ID">Episode title</a></li>'
EPISODE_1_HREF = "https://youtube.com/shorts/NH9Jx3Jh28A"
EPISODE_1_TITLE = "Florida Lighting Controls: Which Energy Code Applies Now?"
EPISODE_1 = f'<li><a href="{EPISODE_1_HREF}">{EPISODE_1_TITLE}</a></li>'
EPISODE_2_HREF = "https://youtube.com/shorts/R9B15oZF_Rk"
EPISODE_2_TITLE = "Florida Lighting Controls: Is Plug-Load Control Required?"
EPISODE_2 = f'<li><a href="{EPISODE_2_HREF}">{EPISODE_2_TITLE}</a></li>'
EPISODE_3_HREF = "https://youtube.com/shorts/ZFQOWlmhil4"
EPISODE_3_TITLE = "Florida Lighting Controls: Is the Secondary Sidelit Zone Required?"
EPISODE_3 = f'<li><a href="{EPISODE_3_HREF}">{EPISODE_3_TITLE}</a></li>'


def articles(html):
    return re.findall(r"<article\b([^>]*)>(.*?)</article>", html, flags=re.S)


def attr(attrs, name):
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else ""


def plain(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    return text.replace("&amp;", "&").replace("&middot;", "·").strip()


def text_of(fragment, tag):
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", fragment, flags=re.S)
    return plain(match.group(1)) if match else ""


def price_of(fragment):
    match = re.search(r'class="price"[^>]*>(.*?)</p>', fragment, flags=re.S)
    amount = re.search(r"\$\d+", plain(match.group(1)) if match else "")
    return amount.group(0) if amount else ""


def hrefs(fragment, class_name):
    return re.findall(rf'<a class="{class_name}" href="([^"]+)"([^>]*)>', fragment)


class LightingControlsSectionTest(unittest.TestCase):
    def setUp(self):
        self.section = HTML.split('id="lighting-controls"', 1)[1].split('id="articles"', 1)[0]
        panel = self.section.split('<div class="shorts-panel">', 1)[1].split('<p class="related-reading">', 1)[0]
        self.videos = '<div class="shorts-panel">' + panel
        self.cards = {attr(attrs, "id"): body for attrs, body in articles(self.section + LEARN)}
        # The episode example is a comment, not a live link.
        self.live = re.sub(r"<!--.*?-->", "", self.videos, flags=re.S)

    def test_section_order_and_nav(self):
        self.assertLess(HTML.index('id="preview"'), HTML.index('id="lighting-controls"'))
        self.assertIn('id="free-quiz"', HTML)
        self.assertIn("Lighting Controls", text_of(self.section, "h2"))
        self.assertIn("Florida commercial lighting controls for drafters and designers.", self.section)
        self.assertIn('href="#florida-lighting-article"', self.section)
        self.assertIn('href="#videos"', HTML)
        self.assertIn('href="#articles"', HTML)
        header = HTML.split('aria-label="Main"', 1)[1].split("</nav>", 1)[0]
        categories = HTML.split('aria-label="Product categories"', 1)[1].split("</nav>", 1)[0]
        self.assertIn('href="#lighting-controls"', header)
        self.assertIn('href="#lighting-controls"', categories)
        self.assertIn("#lighting-controls { scroll-margin-top: 9rem; }", CSS)
        desktop = CSS.split("@media (min-width: 768px)", 1)[1].split("}", 1)[0]
        self.assertIn("#lighting-controls,", desktop)

    def test_shorts_shelf_lists_episode_one(self):
        self.assertIn("Florida Lighting Controls in 30 Seconds", self.videos)
        self.assertIn("A series of 30-second YouTube Shorts. More episodes are coming.", self.videos)
        self.assertIn(EPISODE_LINE, self.videos)
        episodes = self.live.split('class="episode-list"', 1)[1].split("</ol>", 1)[0]
        soon = '<li><span class="episode-soon">More episodes coming</span></li>'
        self.assertIn(EPISODE_1, episodes)
        self.assertIn(EPISODE_2, episodes)
        self.assertIn(EPISODE_3, episodes)
        self.assertLess(episodes.index(EPISODE_1), episodes.index(EPISODE_2))
        self.assertLess(episodes.index(EPISODE_2), episodes.index(EPISODE_3))
        self.assertLess(episodes.index(EPISODE_3), episodes.index(soon))
        self.assertEqual(episodes.count("<li>"), 4)
        self.assertIn(".episode-list a", CSS)
        self.assertIn(".episode-soon", CSS)
        youtube = hrefs(self.videos, "btn btn-primary")
        self.assertIn(YOUTUBE, [href for href, _ in youtube])
        for href, extra in youtube:
            if href == YOUTUBE:
                self.assertIn('target="_blank"', extra)
                self.assertIn('rel="noopener"', extra)

    def test_article_links(self):
        card = self.cards["florida-lighting-article"]
        self.assertNotIn('id="florida-lighting-article"', self.section)
        self.assertIn('href="#florida-lighting-article"', self.section)
        self.assertIn(">Read the related article<", self.section)
        self.assertEqual(text_of(card, "h3"), ARTICLE)
        primary = hrefs(card, "btn btn-primary")
        secondary = hrefs(card, "btn btn-secondary")
        title = hrefs(card, "card-title-link")
        self.assertEqual([href for href, _ in primary], [MEDIUM])
        self.assertEqual([href for href, _ in secondary], [SUBSTACK])
        self.assertEqual([href for href, _ in title], [MEDIUM])
        self.assertIn("Read on Medium", card)
        self.assertIn("Read on Substack", card)
        for _, extra in primary + secondary + title:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)

    def test_permit_kit_uses_the_existing_price(self):
        card = self.cards["lighting-permit-kit"]
        original = [body for attrs, body in articles(HTML) if attr(attrs, "id") == "permit-qaqc"]
        self.assertEqual(len(original), 1)
        self.assertEqual(text_of(card, "h3"), "Commercial Permit-Set QA/QC + Pre-Submittal Review Kit")
        self.assertEqual(price_of(card), "$29")
        self.assertEqual(price_of(card), price_of(original[0]))
        self.assertIn(">Buy for $29<", card)
        self.assertIn(">Also on Etsy<", card)
        self.assertIn('href="#commercial-permitting"', card)
        primary = hrefs(card, "btn btn-primary")
        secondary = hrefs(card, "btn btn-secondary")
        title = hrefs(card, "card-title-link")
        self.assertEqual([href for href, _ in primary], [BMAC])
        self.assertEqual([href for href, _ in secondary], [ETSY])
        self.assertEqual([href for href, _ in title], [BMAC])
        for _, extra in primary + secondary + title:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)
        self.assertIn('src="images/commercial-permit-set-qaqc-cover.jpg"', card)
        self.assertIn('class="card-image"', card)

    def test_disclaimer_and_no_invented_claims(self):
        self.assertIn(DISCLAIMER, plain(self.section))
        for phrase in (
            "code-compliant",
            "code compliant",
            "guaranteed",
            "will be approved",
            "20% off",
            "25.60",
        ):
            self.assertNotIn(phrase, self.section)
        self.assertIn(EPISODE_1_HREF, self.live)
        self.assertIn(EPISODE_2_HREF, self.live)
        self.assertIn(EPISODE_3_HREF, self.live)
        self.assertNotIn("VIDEO_ID", self.live)

    def test_live_links_are_absolute(self):
        for href in re.findall(r'href="([^"]+)"', self.live):
            if href.startswith("#"):
                self.assertIn(f'id="{href[1:]}"', LEARN)
                continue
            self.assertTrue(href.startswith("https://"), href)
            self.assertNotIn("VIDEO_ID", href)
            self.assertNotEqual(href, "https://")
        for href in re.findall(r'href="([^"]+)"', self.section):
            if href.startswith("#"):
                self.assertIn(f'id="{href[1:]}"', HTML)
                continue
            if href.startswith("learn.html#"):
                self.assertIn(f'id="{href.split("#", 1)[1]}"', LEARN)
                continue
            self.assertTrue(href.startswith("https://"), href)
