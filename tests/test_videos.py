"""Video Tutorials section: long-form YouTube videos, newest first within each topic.

The channel videos tab lists 13 public long-form videos. None of them are
Lighting Controls (those are Shorts), so the section has two topic groups.

Run from the repo root: python3 -m unittest tests/test_videos.py
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

CHANNEL = "https://www.youtube.com/@ZeroWasteDrafting"
SHORTS = "https://www.youtube.com/@ZeroWasteDrafting/shorts"
LEAN = (
    ("_gbqWsdQsKs", "Fill Out a DMAIC Project Charter + SIPOC in 10 Minutes (Lean Six Sigma)"),
    ("SZTEeWy7mQg", "Cp vs Cpk vs Ppk in 60 Seconds (Lean Six Sigma Green Belt)"),
    ("-il07SqjbUs", "5 Whys in 45 Seconds: Find the Root Cause (Lean Six Sigma)"),
    ("cKwAS7rdQgo", "The 8 Wastes of Lean in 60 Seconds (DOWNTIME Explained)"),
    ("Cwk2REDGxJk", "DMAIC in 60 Seconds | Lean Six Sigma Explained (Animated)"),
)
CAD = (
    ("prBmRY3U4S0", "How I Handle Client Redlines on Freelance CAD Work (4 Steps)"),
    ("yW8NzI9pf68", "AutoCAD Page Setups for Commercial Sheet Sets (4 Steps)"),
    ("noAW4EDjARg", "Revit View Templates for Commercial Projects (4 Steps)"),
    ("I3tNTx1TU2Y", "How I'd Price Freelance Commercial CAD Work (4 Steps, No Guesswork)"),
    ("cD8n8tNSbCY", "Clean AutoCAD Layer Standards in 60 Seconds (Commercial Drawings)"),
    ("KCSBgGuxyEg", "5 AutoCAD Habits That Save Hours on Commercial Drawings"),
    ("yJJRLVAYKHA", "How to Land Your First Freelance CAD Client (4 Honest Steps)"),
    ("QLCF0EfdhRA", "Revit Worksets in 60 Seconds | Worksharing for Commercial Projects"),
)


def articles(html):
    return re.findall(r"<article\b([^>]*)>(.*?)</article>", html, flags=re.S)


def attr(attrs, name):
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else ""


def plain(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    text = text.replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def text_of(fragment, tag):
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", fragment, flags=re.S)
    return plain(match.group(1)) if match else ""


class VideoTutorialsTest(unittest.TestCase):
    def setUp(self):
        self.section = HTML.split('id="videos"', 1)[1].split('id="free-quiz"', 1)[0]
        self.cards = [(attr(attrs, "id"), body) for attrs, body in articles(self.section)]

    def test_section_and_nav_sit_beside_articles(self):
        self.assertLess(HTML.index('id="articles"'), HTML.index('id="videos"'))
        self.assertLess(HTML.index('id="videos"'), HTML.index('id="free-quiz"'))
        self.assertEqual(text_of(self.section, "h2"), "Video Tutorials")
        self.assertIn(
            "Full-length YouTube tutorials on Lean Six Sigma and commercial CAD and Revit.",
            self.section,
        )
        header = HTML.split('aria-label="Main"', 1)[1].split("</nav>", 1)[0]
        hrefs = re.findall(r'href="(#[^"]+)"', header)
        self.assertLess(hrefs.index("#articles"), hrefs.index("#videos"))
        self.assertLess(hrefs.index("#videos"), hrefs.index("#faq"))
        topics = re.findall(r'class="video-topic"[^>]*>(.*?)</h3>', self.section)
        self.assertEqual([plain(topic) for topic in topics], ["Lean Six Sigma", "CAD & Revit"])
        self.assertIn(".video-thumb img", CSS)
        self.assertIn("aspect-ratio: 16 / 9", CSS)

    def test_long_form_cards_match_the_channel_videos(self):
        expected = LEAN + CAD
        self.assertEqual(len(self.cards), 13)
        self.assertEqual(len(self.cards), len(expected))
        lean_html, cad_html = self.section.split('id="videos-cad"', 1)
        lean_ids = [attr(attrs, "id") for attrs, _ in articles(lean_html)]
        cad_ids = [attr(attrs, "id") for attrs, _ in articles(cad_html)]
        self.assertEqual(lean_ids, [f"video-{vid}" for vid, _ in LEAN])
        self.assertEqual(cad_ids, [f"video-{vid}" for vid, _ in CAD])
        for (card_id, body), (vid, title) in zip(self.cards, expected):
            watch = f"https://www.youtube.com/watch?v={vid}"
            thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            self.assertEqual(card_id, f"video-{vid}")
            self.assertEqual(text_of(body, "h3"), title)
            self.assertNotIn('class="price"', body)
            self.assertNotIn("buymeacoffee.com", body)
            self.assertNotIn("<iframe", body)
            self.assertNotIn("/embed", body)
            img = re.search(r"<img\b[^>]*>", body).group(0)
            self.assertIn(f'src="{thumb}"', img)
            self.assertIn('loading="lazy"', img)
            self.assertIn('width="480"', img)
            self.assertIn('height="360"', img)
            self.assertIn(f'alt="{title}"', img)
            links = re.findall(r'<a class="([^"]*)" href="([^"]+)"([^>]*)>', body)
            self.assertEqual(
                [(cls, href) for cls, href, _ in links],
                [("video-thumb", watch), ("card-title-link", watch)],
            )
            for _, href, extra in links:
                self.assertEqual(href, watch)
                self.assertNotIn("/shorts", href)
                self.assertIn('target="_blank"', extra)
                self.assertIn('rel="noopener"', extra)

    def test_section_ends_with_shorts_and_subscribe_links(self):
        actions = self.section.split('class="video-actions"', 1)[1]
        self.assertLess(self.section.index("video-card"), self.section.index("video-actions"))
        links = re.findall(r'<a class="([^"]*)" href="([^"]+)"([^>]*)>(.*?)</a>', actions)
        self.assertEqual(
            [(cls, href, plain(text)) for cls, href, _, text in links],
            [
                ("btn btn-secondary", SHORTS, "Watch all Shorts"),
                ("btn btn-primary", CHANNEL, "Subscribe"),
            ],
        )
        for _, _, extra, _ in links:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)
        self.assertNotIn("<iframe", self.section)
        self.assertNotIn("youtube.com/embed", self.section)
        self.assertEqual(self.section.count("/shorts"), 1)
