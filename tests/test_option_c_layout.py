"""Option C pages: shop catalog, free resources, articles, and shared nav.

Run from the repo root: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "shop.html", "free.html", "learn.html"]
HTML = {name: (ROOT / name).read_text(encoding="utf-8") for name in PAGES}
HOME = HTML["index.html"]
SHOP = HOME
FREE = HOME
LEARN = HOME
ALL = "\n".join(HTML.values())

BANNED = (
    "https://buymeacoffee.com/robinwolfson/e/593903",
    "https://buymeacoffee.com/robinwolfson/e/593901",
    "https://buymeacoffee.com/robinwolfson/e/593132",
)


def articles(html):
    return re.findall(r"<article\b([^>]*)>(.*?)</article>", html, flags=re.S)


def attr(attrs, name):
    match = re.search(rf'{name}="([^"]*)"', attrs)
    return match.group(1) if match else ""


def plain(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    text = text.replace("&amp;", "&").replace("&middot;", "·").replace("&#39;", "'")
    return re.sub(r"\s+", " ", text).strip()


def price_of(fragment):
    match = re.search(r'class="price"[^>]*>(.*?)</p>', fragment, flags=re.S)
    text = plain(match.group(1)) if match else ""
    amount = re.search(r"\$\d+", text)
    if amount:
        return amount.group(0)
    if "Free" in text:
        return "Free"
    return ""


class OptionCLayoutTest(unittest.TestCase):
    def test_nav_and_tab_bar_on_every_page(self):
        header = HOME.split('aria-label="Main"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(
            re.findall(r'href="([^"]+)"', header),
            [
                "#products",
                "#bundles",
                "#extras",
                "#lighting-controls",
                "#articles",
                "#videos",
                "#free-quiz",
                "#free-revit-sheet",
                "#about",
                "#faq",
            ],
        )
        self.assertIn("<main", HOME)
        self.assertIn('class="skip-link"', HOME)
        self.assertIn('href="https://x.com/RobinCWolfson"', HOME)
        self.assertIn("X (@RobinCWolfson)", HOME)
        self.assertIn("Video Tutorials", HOME)
        for name in ("shop.html", "free.html", "learn.html"):
            self.assertIn('location.replace("index.html#', HTML[name], name)

    def test_shop_keeps_every_price_and_link(self):
        expected = {
            "Lean Six Sigma Green Belt Study Guide + 75-Question Practice Exam": (
                "$11",
                "https://buymeacoffee.com/robinwolfson/e/593083",
                "https://zerowastedrafting.etsy.com/listing/4609955222/six-sigma-green-belt-study-guide-2026-75",
            ),
            "The Lean Six Sigma Toolkit": (
                "$9",
                "https://buymeacoffee.com/robinwolfson/e/593067",
                "https://zerowastedrafting.etsy.com/listing/4609933231/dmaic-toolkit-lean-six-sigma-templates",
            ),
            "The Freelance CAD Drafting Starter Guide": (
                "$9",
                "https://buymeacoffee.com/robinwolfson/e/593100",
                "https://zerowastedrafting.etsy.com/listing/4609956156/freelance-cad-drafting-guide-commercial",
            ),
            "Commercial AutoCAD Starter Kit": (
                "$14",
                "https://buymeacoffee.com/robinwolfson/e/597741",
                "https://zerowastedrafting.etsy.com/listing/4615757637/commercial-autocad-starter-kit-for",
            ),
            "The Commercial AutoCAD Standards Pack": (
                "$13",
                "https://buymeacoffee.com/robinwolfson/e/597743",
                "https://zerowastedrafting.etsy.com/listing/4615758689/autocad-standards-pack-commercial",
            ),
            "AI Prompt Pack for CAD and Revit Drafters": (
                "$9",
                "https://buymeacoffee.com/robinwolfson/e/599857",
                "https://www.etsy.com/listing/4620552083/ai-prompt-pack-for-cad-and-revit",
            ),
            "The Freelance Revit Playbook": (
                "$13",
                "https://buymeacoffee.com/robinwolfson/e/597740",
                "https://zerowastedrafting.etsy.com/listing/4615769344/the-freelance-revit-playbook-scope-price",
            ),
            "The Commercial Revit Template & Standards Pack": (
                "$11",
                "https://buymeacoffee.com/robinwolfson/e/593881",
                "https://zerowastedrafting.etsy.com/listing/4609957298/revit-template-standards-for-commercial",
            ),
            "Commercial Revit Template & Standards Pack, Classroom License": (
                "$39",
                "https://buymeacoffee.com/robinwolfson/e/594979",
                None,
            ),
            "Studio Team License": (
                "$59",
                "https://buymeacoffee.com/robinwolfson/e/595451",
                None,
            ),
            "Office Team License": (
                "$99",
                "https://buymeacoffee.com/robinwolfson/e/595452",
                None,
            ),
            "11+ seats": ("", "mailto:robinwolfson.drafting@gmail.com", None),
            "Lean Six Sigma Bundle": (
                "$16",
                "https://buymeacoffee.com/robinwolfson/e/593126",
                "https://zerowastedrafting.etsy.com/listing/4609959548/six-sigma-green-belt-bundle-study-guide",
            ),
            "The Commercial AutoCAD Bundle": (
                "$39",
                "https://buymeacoffee.com/robinwolfson/e/597753",
                "https://zerowastedrafting.etsy.com/listing/4615785177/commercial-autocad-bundle-freelance-cad",
            ),
            "The Freelance Revit Bundle": (
                "$26",
                "https://buymeacoffee.com/robinwolfson/e/597754",
                "https://zerowastedrafting.etsy.com/listing/4615786025/freelance-revit-bundle-commercial",
            ),
            "Commercial Permit-Set QA/QC + Pre-Submittal Review Kit": (
                "$21",
                "https://buymeacoffee.com/robinwolfson/e/595488",
                "https://zerowastedrafting.etsy.com/listing/4611461235/commercial-permit-set-qaqc-checklist-pre",
            ),
            "2027 Drafting Scenes Wall Calendar": (
                "$36",
                "https://www.etsy.com/listing/4621033798",
                None,
            ),
            "Revit Naming Standards Poster (18x24)": (
                "$29",
                "https://www.etsy.com/listing/4619695521",
                None,
            ),
            "CAD Drafting Standards Poster (18x24)": (
                "$29",
                "https://www.etsy.com/listing/4620179623",
                None,
            ),
            "Florida Lighting Controls Pre-Submittal Kit (nLight and nLight AIR)": (
                "$19",
                "https://buymeacoffee.com/robinwolfson/e/599727",
                "https://www.etsy.com/listing/4620381518/florida-nlight-lighting-controls-kit",
            ),
        }
        # The permit kit is listed twice. The lighting card uses the short Etsy URL.
        lighting_etsy = "https://www.etsy.com/listing/4611461235"
        seen = {}
        catalog = HOME.split('id="articles"', 1)[0]
        for attrs, body in articles(catalog):
            title = plain(re.search(r"<h3\b[^>]*>(.*?)</h3>", body, flags=re.S).group(1))
            price = price_of(body)
            links = re.findall(r'href="([^"]+)"', body)
            card_id = attr(attrs, "id")
            if title == "Commercial Permit-Set QA/QC + Pre-Submittal Review Kit" and card_id == "lighting-permit-kit":
                self.assertEqual(price, "$21")
                self.assertIn("https://buymeacoffee.com/robinwolfson/e/595488", links)
                self.assertIn(lighting_etsy, links)
                self.assertNotIn("buymeacoffee.com/robinwolfson/e/593", body.replace("/e/595488", ""))
                continue
            self.assertIn(title, expected, title)
            want_price, buy, etsy = expected[title]
            self.assertEqual(price, want_price, title)
            self.assertIn(buy, links, title)
            if etsy:
                self.assertIn(etsy, links, title)
            if title in (
                "2027 Drafting Scenes Wall Calendar",
                "Revit Naming Standards Poster (18x24)",
                "CAD Drafting Standards Poster (18x24)",
            ):
                self.assertNotIn("buymeacoffee.com", body, title)
            seen[title] = True
        self.assertEqual(set(seen), set(expected))
        quiz = HOME.split('id="free-quiz"', 1)[1].split('id="free-revit-sheet"', 1)[0]
        self.assertIn("Green Belt Practice Quiz: 10 free questions", quiz)
        self.assertIn("https://buymeacoffee.com/robinwolfson/e/593113", quiz)
        # Both permit cards plus every other product.
        self.assertGreaterEqual(len(list(articles(catalog))), len(expected))

    def test_search_filter_and_sort_markup(self):
        shop = HTML["shop.html"]
        self.assertIn("lss:", shop)
        self.assertIn("lean-six-sigma", shop)
        self.assertIn("index.html#", shop)
        free = HTML["free.html"]
        self.assertIn("free-quiz", free)
        learn = HTML["learn.html"]
        self.assertIn("articles", learn)
        self.assertNotRegex(HOME, r'<article\b[^>]*\shidden\b')

    def test_free_items_on_home_and_free_resources(self):
        quiz = "https://buymeacoffee.com/robinwolfson/e/593113"
        medium = "dont-copy-a-2021-iecc-lighting-controls-cheat-sheet-onto-a-florida-permit-set-bfe1dcf85039"
        substack = "https://robinwolfson.substack.com/p/dont-copy-a-2021-iecc-lighting-controls"
        shorts = (
            "https://youtube.com/shorts/NH9Jx3Jh28A",
            "https://youtube.com/shorts/R9B15oZF_Rk",
        )
        for html in (HOME, FREE):
            self.assertIn(quiz, html)
            self.assertIn('data-form="8TQkZA"', html)
            self.assertIn("Commercial Revit naming cheat sheet", html)
            self.assertIn("ml('account', '2771828')", html)
            self.assertIn("https://www.youtube.com/@ZeroWasteDrafting", html)
        self.assertIn(
            "asq-vs-iassc-vs-cssc-which-green-belt-certification-should-you-actually-take-8d0041754f11",
            HOME,
        )
        self.assertIn("https://www.youtube.com/watch?v=_gbqWsdQsKs", HOME)
        self.assertIn(medium, FREE)
        self.assertIn(substack, FREE)
        for short in shorts:
            self.assertIn(short, FREE)
        self.assertIn("https://youtube.com/shorts/ZFQOWlmhil4", FREE)
        self.assertIn('id="start-free"', HOME)
        self.assertIn('id="free-quiz"', HOME)
        self.assertIn('id="free-revit-sheet"', HOME)
        self.assertNotIn("you@firm.com", ALL)
        self.assertNotIn("Send me the PDF", ALL)

    def test_articles_and_videos_keep_current_content(self):
        articles_html = LEARN.split('id="articles"', 1)[1].split('id="videos"', 1)[0]
        videos = LEARN.split('id="videos"', 1)[1]
        self.assertIn("ASQ vs IASSC vs CSSC: Which Green Belt Certification Should You Actually Take?", articles_html)
        self.assertEqual(len(set(re.findall(r"https://medium.com/@robinwolfson\.drafting/[a-z0-9-]+", LEARN))), 6)
        self.assertEqual(len(set(re.findall(r"youtube\.com/watch\?v=([A-Za-z0-9_-]+)", LEARN))), 14)
        self.assertIn("https://www.youtube.com/watch?v=h29bPQ2JZKE", LEARN)
        self.assertIn("https://youtube.com/shorts/2V-zXY_i6O4", LEARN)
        self.assertIn("ZFQOWlmhil4", LEARN)
        self.assertIn("Read on Medium", articles_html)
        self.assertIn("Read on Substack", articles_html)
        self.assertIn("Video Tutorials", videos)
        self.assertIn("Florida Lighting Controls in 30 Seconds", LEARN)
        self.assertIn("More episodes coming", LEARN)
        self.assertIn(
            '<li><a href="https://www.youtube.com/shorts/VIDEO_ID">Episode title</a></li>',
            LEARN,
        )
        self.assertIn('id="faq"', HOME)
        self.assertIn("Physical print-on-demand items, sold on Etsy. The calendar is also on Amazon.", SHOP)
        self.assertIn("https://www.amazon.com/dp/B0HT3V8KF7", SHOP)
        self.assertIn("Paperback on Amazon — $24.99", SHOP)
        self.assertIn("https://www.amazon.com/dp/B0HSVXGLQF", SHOP)
        self.assertIn("Buy on Amazon — $39.99", SHOP)
        self.assertIn('id="preview"', SHOP)
        self.assertIn('id="about"', HOME)

    def test_no_banned_or_invented_checkout_links(self):
        for url in BANNED:
            self.assertNotIn(url, ALL)
        for name, html in HTML.items():
            self.assertNotIn("/e/593903", html, name)
            self.assertNotIn("/e/593901", html, name)
            self.assertNotIn("/e/593132", html, name)


if __name__ == "__main__":
    unittest.main()
