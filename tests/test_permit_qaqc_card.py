"""Card and asset checks for the Commercial Permit-Set QA/QC kit.

Run from the repo root: python3 -m unittest tests/test_permit_qaqc_card.py
"""

import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

# Buy Me a Coffee prices and checkouts already on the site. The new card must
# not rewrite these.
EXISTING = {
    "Lean Six Sigma Green Belt Study Guide + 75-Question Practice Exam": (
        "$15",
        "https://buymeacoffee.com/robinwolfson/e/593083",
        "https://zerowastedrafting.etsy.com/listing/4609955222/six-sigma-green-belt-study-guide-2026-75",
    ),
    "The Lean Six Sigma Toolkit": (
        "$12",
        "https://buymeacoffee.com/robinwolfson/e/593067",
        "https://zerowastedrafting.etsy.com/listing/4609933231/dmaic-toolkit-lean-six-sigma-templates",
    ),
    "The Freelance CAD Drafting Starter Guide": (
        "$12",
        "https://buymeacoffee.com/robinwolfson/e/593100",
        "https://zerowastedrafting.etsy.com/listing/4609956156/freelance-cad-drafting-guide-commercial",
    ),
    "The Commercial Revit Template & Standards Pack": (
        "$15",
        "https://buymeacoffee.com/robinwolfson/e/593881",
        "https://zerowastedrafting.etsy.com/listing/4609957298/revit-template-standards-for-commercial",
    ),
    "Commercial Revit Template & Standards Pack, Classroom License": (
        "$49",
        "https://buymeacoffee.com/robinwolfson/e/594979",
        None,
    ),
    "Lean Six Sigma Bundle": (
        "$22",
        "https://buymeacoffee.com/robinwolfson/e/593126",
        "https://zerowastedrafting.etsy.com/listing/4609959548/six-sigma-green-belt-bundle-study-guide",
    ),
    "CAD + Revit Bundle": (
        "$22",
        "https://buymeacoffee.com/robinwolfson/e/593901",
        "https://zerowastedrafting.etsy.com/listing/4609960632/revit-and-cad-drafting-bundle-commercial",
    ),
    "Studio Team License": (
        "$79",
        "https://buymeacoffee.com/robinwolfson/e/595451",
        None,
    ),
    "Office Team License": (
        "$139",
        "https://buymeacoffee.com/robinwolfson/e/595452",
        None,
    ),
}

BMAC = "https://buymeacoffee.com/robinwolfson/e/595488"
ETSY = "https://zerowastedrafting.etsy.com/listing/4611461235/commercial-permit-set-qaqc-checklist-pre"
COVER = ROOT / "images" / "commercial-permit-set-qaqc-cover.jpg"


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
    return re.findall(
        rf'<a class="{class_name}" href="([^"]+)"([^>]*)>',
        fragment,
    )


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


class PermitKitCardTest(unittest.TestCase):
    def setUp(self):
        found = [body for attrs, body in articles(HTML) if attr(attrs, "id") == "permit-qaqc"]
        self.assertEqual(len(found), 1)
        self.card = found[0]

    def test_card_sits_with_the_cad_and_revit_products(self):
        product_html = HTML.split('id="products"', 1)[1].split('id="preview"', 1)[0]
        titles = [text_of(body, "h3") for _, body in articles(product_html)]
        self.assertEqual(
            titles,
            [
                "Lean Six Sigma Green Belt Study Guide + 75-Question Practice Exam",
                "The Lean Six Sigma Toolkit",
                "The Freelance CAD Drafting Starter Guide",
                "The Commercial Revit Template & Standards Pack",
                "Commercial Revit Template & Standards Pack, Classroom License",
                "Commercial Permit-Set QA/QC + Pre-Submittal Review Kit",
                "Studio Team License",
                "Office Team License",
                "11+ seats",
            ],
        )

    def test_price_formats_and_store_links(self):
        self.assertEqual(text_of(self.card, "h3"), "Commercial Permit-Set QA/QC + Pre-Submittal Review Kit")
        self.assertEqual(price_of(self.card), "$29")
        self.assertNotIn("$32", self.card)
        self.assertNotIn("25.60", self.card)
        self.assertIn("Guide PDF", self.card)
        self.assertIn("Excel QA/QC workbook", self.card)
        self.assertIn("33-field", self.card)
        self.assertIn("fillable PDF", self.card)
        self.assertIn("DOCX", self.card)
        self.assertIn('src="images/commercial-permit-set-qaqc-cover.jpg"', self.card)
        self.assertIn('width="800"', self.card)
        self.assertIn('height="800"', self.card)

        primary = hrefs(self.card, "btn btn-primary")
        secondary = hrefs(self.card, "btn btn-secondary")
        self.assertEqual([href for href, _ in primary], [BMAC])
        self.assertEqual([href for href, _ in secondary], [ETSY])
        for _, extra in primary + secondary:
            self.assertIn('target="_blank"', extra)
            self.assertIn('rel="noopener"', extra)
        self.assertNotIn("downloads/", self.card)
        self.assertIn("Buy for $29", self.card)
        self.assertIn("Also on Etsy", self.card)

    def test_no_approval_or_sale_claims(self):
        self.assertIn("Not legal or code advice", self.card)
        self.assertIn("not a code review", self.card)
        self.assertIn("not a guarantee of permit approval or code compliance", self.card)
        for phrase in (
            "25.60",
            "Nov 18",
            "November 18",
            "20% off",
            "20% sale",
            "guaranteed",
            "code-compliant",
            "code compliant",
            "will be approved",
        ):
            self.assertNotIn(phrase, HTML)

    def test_existing_products_and_bundles_unchanged(self):
        seen = {}
        for _, body in articles(HTML):
            title = text_of(body, "h3")
            if title not in EXISTING:
                continue
            price = price_of(body)
            buy = hrefs(body, "btn btn-primary") or hrefs(body, "btn btn-primary btn-block")
            etsy = hrefs(body, "btn btn-secondary")
            seen[title] = (price, buy[0][0], etsy[0][0] if etsy else None)
        self.assertEqual(seen, EXISTING)

    def test_cover_matches_image_convention(self):
        self.assertTrue(COVER.is_file())
        self.assertEqual(jpeg_size(COVER), (800, 800))
        self.assertLess(COVER.stat().st_size, 180_000)
        self.assertNotIn("user", COVER.name.lower())

    def test_no_paid_files_or_user_named_paths(self):
        paid = {".zip", ".xlsx", ".docx", ".xls", ".xlsm"}
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            self.assertNotIn("user", path.name.lower(), path)
            self.assertNotIn(path.suffix.lower(), paid, path)
        downloads = sorted(p.name for p in (ROOT / "downloads").iterdir())
        self.assertEqual(downloads, ["Commercial-Revit-Naming-Cheat-Sheet-Zero-Waste-Drafting.pdf"])

    def test_desktop_grid_gives_every_product_card_the_same_width(self):
        self.assertIn(".grid > .card { grid-column: span 2; }", CSS)
        self.assertNotIn("card-revit { grid-column: span 3", CSS)
        self.assertNotIn("#permit-qaqc { grid-column:", CSS)
        self.assertNotIn("#studio-team-license { grid-column:", CSS)
        self.assertNotIn("#office-team-license { grid-column:", CSS)

    def test_firm_team_licenses(self):
        product_html = HTML.split('id="products"', 1)[1].split('id="preview"', 1)[0]
        by_id = {attr(attrs, "id"): body for attrs, body in articles(product_html)}
        studio = by_id["studio-team-license"]
        office = by_id["office-team-license"]
        quote = by_id["team-license-quote"]

        self.assertLess(product_html.index('id="classroom-license"'), product_html.index('id="studio-team-license"'))
        self.assertLess(product_html.index('id="studio-team-license"'), product_html.index('id="office-team-license"'))
        self.assertLess(product_html.index('id="office-team-license"'), product_html.index('id="team-license-quote"'))

        for card, price, href in (
            (studio, "$79", "https://buymeacoffee.com/robinwolfson/e/595451"),
            (office, "$139", "https://buymeacoffee.com/robinwolfson/e/595452"),
        ):
            self.assertEqual(price_of(card), price)
            self.assertIn("Commercial Revit Template &amp; Standards Pack", card)
            self.assertIn("The Freelance CAD Drafting Starter Guide", card)
            self.assertNotIn("etsy", card.lower())
            self.assertNotIn("btn-secondary", card)
            primary = hrefs(card, "btn btn-primary btn-block")
            self.assertEqual([link for link, _ in primary], [href])
            for _, extra in primary:
                self.assertIn('target="_blank"', extra)
                self.assertIn('rel="noopener"', extra)

        self.assertIn("Up to 5 users", studio)
        self.assertIn("up to 5", studio)
        self.assertIn("Up to 10 users", office)
        self.assertIn("up to 10", office)
        self.assertNotIn("$79", office)
        self.assertNotIn("$139", studio)
        self.assertNotIn('class="price"', quote)
        self.assertNotIn("buymeacoffee.com", quote)
        self.assertNotIn("etsy", quote.lower())
        self.assertEqual(quote.count("mailto:robinwolfson.drafting@gmail.com"), 2)
        self.assertIn("11 or more seats", quote)
        self.assertIn("Quoted by email", quote)
        quote_rule = CSS.split(".grid > .team-quote {", 1)[1].split("}", 1)[0]
        self.assertIn("grid-column: 1 / -1;", quote_rule)
        self.assertIn("flex-direction: row;", quote_rule)


if __name__ == "__main__":
    unittest.main()
