"""Extras section: physical prints sold on Etsy, with the calendar also on Amazon.

Run from the repo root: python3 -m unittest tests/test_extras_section.py
"""

import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
HOME = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

CALENDAR_URL = "https://www.etsy.com/listing/4621033798"
CALENDAR_AMAZON_URL = "https://www.amazon.com/dp/B0HSVXGLQF"
POSTER_URL = "https://www.etsy.com/listing/4619695521"
CAD_POSTER_URL = "https://www.etsy.com/listing/4620179623"


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


def jpeg_size(path):
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise AssertionError(f"{path.name} is not a JPEG")
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            raise AssertionError("broken JPEG marker")
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        if marker in (0xD8, 0xD9):
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + length
    raise AssertionError("JPEG size not found")


class ExtrasSectionTest(unittest.TestCase):
    def setUp(self):
        self.extras = HTML.split('id="extras"', 1)[1].split('id="preview"', 1)[0]
        self.cards = {attr(attrs, "id"): body for attrs, body in articles(self.extras)}

    def test_section_sits_between_the_guides_and_the_preview(self):
        self.assertLess(HTML.index('id="products"'), HTML.index('id="extras"'))
        self.assertLess(HTML.index('id="extras"'), HTML.index('id="preview"'))
        self.assertIn(
            "Physical print-on-demand items, sold on Etsy. The calendar is also on Amazon.",
            self.extras,
        )
        self.assertNotIn("sold only on Etsy", self.extras)
        self.assertEqual(
            [text_of(body, "h3") for body in self.cards.values()],
            [
                "2027 Drafting Scenes Wall Calendar",
                "Revit Naming Standards Poster (18x24)",
                "CAD Drafting Standards Poster (18x24)",
            ],
        )

    def test_nav_links_keep_existing_order_and_add_extras(self):
        header = HTML.split('aria-label="Main"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(
            re.findall(r'href="([^"]+)"', header),
            ["#products", "#bundles", "#extras", "#lighting-controls", "#articles", "#videos", "#free-quiz", "#free-revit-sheet", "#about", "#faq"],
        )
        categories = HTML.split('aria-label="Product categories"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(
            re.findall(r'href="(#[^"]+)"', categories),
            [
                "#lean-six-sigma",
                "#cad",
                "#revit",
                "#bundles",
                "#commercial-permitting",
                "#extras",
                "#lighting-controls",
            ],
        )

    def test_cards_are_etsy_only(self):
        expected = {
            "drafting-scenes-calendar": {
                "title": "2027 Drafting Scenes Wall Calendar",
                "price": "$36",
                "url": CALENDAR_URL,
                "format": "11x17 wall calendar",
                "copy": "12 bold Revit and CAD drafting scenes, one per month, each with a Revit tip, plus US holidays and moon phases.",
                "src": "images/2027-drafting-scenes-wall-calendar.jpg",
                "width": 913,
                "height": 1400,
                "alt_parts": ("2027 Drafting Scenes", "wireframe", "drafting table"),
            },
            "revit-naming-poster": {
                "title": "Revit Naming Standards Poster (18x24)",
                "price": "$29",
                "url": POSTER_URL,
                "format": "18x24 enhanced matte print",
                "copy": "An enhanced matte print of Revit naming conventions.",
                "src": "images/revit-naming-standards-poster-18x24.jpg",
                "width": 900,
                "height": 1200,
                "alt_parts": ("18 by 24", "Revit Naming Standards", "enhanced matte"),
            },
            "cad-drafting-poster": {
                "title": "CAD Drafting Standards Poster (18x24)",
                "price": "$29",
                "url": CAD_POSTER_URL,
                "format": "18x24 enhanced matte print",
                "copy": "An AutoCAD reference print covering NCS/AIA layer naming, lineweights, text heights, and sheet naming.",
                "src": "images/cad-drafting-standards-poster-18x24.jpg",
                "width": 900,
                "height": 1200,
                "alt_parts": ("18 by 24", "CAD Drafting Standards", "NCS/AIA", "lineweights"),
            },
        }
        self.assertEqual(list(self.cards), list(expected))
        for card_id, spec in expected.items():
            card = self.cards[card_id]
            self.assertEqual(text_of(card, "h3"), spec["title"])
            self.assertEqual(price_of(card), spec["price"])
            self.assertIn(spec["format"], plain(card))
            self.assertIn("plus shipping", plain(card))
            self.assertIn(spec["copy"], plain(card))
            self.assertEqual(card.count(">Buy on Etsy<"), 1)
            self.assertNotIn("Buy Me a Coffee", card)
            self.assertNotIn("buymeacoffee.com", card)
            self.assertNotIn("Also on Etsy", card)
            links = re.findall(r'<a class="([^"]*)" href="([^"]+)"([^>]*)>', card)
            if card_id == "drafting-scenes-calendar":
                self.assertIn(">Buy on Amazon — $39.99<", card)
                self.assertEqual(
                    [(cls, href) for cls, href, _ in links],
                    [
                        ("card-title-link", spec["url"]),
                        ("btn btn-primary", spec["url"]),
                        ("btn btn-secondary", CALENDAR_AMAZON_URL),
                    ],
                )
            else:
                self.assertNotIn("btn-secondary", card)
                self.assertNotIn("amazon.com", card)
                self.assertEqual(
                    [(cls, href) for cls, href, _ in links],
                    [
                        ("card-title-link", spec["url"]),
                        ("btn btn-primary", spec["url"]),
                    ],
                )
            for _, href, extra in links:
                self.assertIn(href, (spec["url"], CALENDAR_AMAZON_URL))
                self.assertNotIn(spec["url"] + "/", card)
                self.assertIn('target="_blank"', extra)
                self.assertIn('rel="noopener"', extra)
            img = re.search(r"<img\b[^>]*>", card).group(0)
            self.assertIn(f'src="{spec["src"]}"', img)
            self.assertIn(f'width="{spec["width"]}"', img)
            self.assertIn(f'height="{spec["height"]}"', img)
            alt = re.search(r'alt="([^"]*)"', img).group(1)
            for part in spec["alt_parts"]:
                self.assertIn(part, alt)
            self.assertGreater(len(alt), len(spec["title"]))
            button = re.search(
                r'<button type="button" class="card-image"[^>]*>.*?</button>',
                card,
                flags=re.S,
            )
            self.assertIsNotNone(button)
            self.assertIn('aria-haspopup="dialog"', button.group(0))
            self.assertIn('aria-controls="product-lightbox"', button.group(0))
            self.assertNotIn("<a ", button.group(0))

        self.assertNotIn("buymeacoffee.com", self.extras)
        self.assertEqual(self.extras.count(CALENDAR_URL), 2)
        self.assertEqual(self.extras.count(CALENDAR_AMAZON_URL), 1)
        self.assertEqual(self.extras.count(POSTER_URL), 2)
        self.assertEqual(self.extras.count(CAD_POSTER_URL), 2)
        self.assertNotEqual(
            (ROOT / "images" / "cad-drafting-standards-poster-18x24.jpg").read_bytes(),
            (ROOT / "images" / "revit-naming-standards-poster-18x24.jpg").read_bytes(),
        )

    def test_images_are_compressed_portrait_jpegs(self):
        files = {
            ROOT / "images" / "2027-drafting-scenes-wall-calendar.jpg": ((913, 1400), 450_000),
            ROOT / "images" / "revit-naming-standards-poster-18x24.jpg": ((900, 1200), 340_000),
            ROOT / "images" / "cad-drafting-standards-poster-18x24.jpg": ((900, 1200), 340_000),
        }
        for path, (size, limit) in files.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(jpeg_size(path), size)
            self.assertLess(path.stat().st_size, limit)
            self.assertGreater(path.stat().st_size, 80_000)
            self.assertNotIn("user", path.name.lower())
        # Portrait frames, not the square crop used on the guide covers.
        self.assertIn("#drafting-scenes-calendar .card-image", CSS)
        self.assertIn("aspect-ratio: 913 / 1400", CSS)
        self.assertIn("aspect-ratio: 3 / 4", CSS)
        self.assertIn("#products,\n#extras,\n#lighting-controls { scroll-margin-top: 9rem; }", CSS)
        desktop = CSS.split("@media (min-width: 768px)", 1)[1].split("}", 1)[0]
        self.assertIn("#extras,", desktop)
        self.assertIn("scroll-margin-top: 5.5rem", desktop)

    def test_faq_covers_digital_downloads_and_shipped_prints(self):
        faq = HOME.split('id="faq"', 1)[1]
        delivery = faq.split("How do I get my files?", 1)[1].split("</details>", 1)[0]
        self.assertNotIn("Nothing is shipped", HOME)
        self.assertNotIn("Nothing is shipped", HTML)
        self.assertIn("instant digital downloads through Buy Me a Coffee", delivery)
        self.assertIn("After checkout you download the files right away.", delivery)
        self.assertIn("Classroom License", delivery)
        self.assertIn(
            "The Extras prints (the calendar and posters) are printed on demand and shipped by our print partner via Etsy, usually in 2-6 business days.",
            delivery,
        )
        self.assertIn("No returns, but damaged items are replaced.", delivery)


if __name__ == "__main__":
    unittest.main()
