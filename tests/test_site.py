import re
import struct
from html.parser import HTMLParser
from pathlib import Path

import pytest
from playwright.sync_api import Page

ROOT = Path(__file__).parent.parent
SITE = ROOT / "index.html"
HTML = SITE.read_text()
SHAMED_LIBRARIES = ["pandas", "requests", "numpy", "django", "flask", "jquery"]
DASHES = ["—", "–"]
WIDTHS = [320, 402, 768, 1100, 1440]
COVER_ANIMATION_MS = 4000


class Tags(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text: list[str] = []
        assert self.tags == [], "a new parser starts with no tags"
        assert self.text == [], "a new parser starts with no text"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        assert tag, "the parser only reports start tags that have a name"
        count = len(self.tags)
        self.tags.append((tag, {name: value or "" for name, value in attrs}))
        assert len(self.tags) == count + 1, "each start tag is recorded exactly once"

    def handle_data(self, data: str) -> None:
        assert self.rawdata, "text only arrives while a document is being fed"
        count = len(self.text)
        self.text.append(data)
        assert len(self.text) == count + 1, "each run of text is recorded exactly once"


def parsed() -> Tags:
    assert HTML.lstrip().startswith("<!doctype html>"), "index.html must start with a doctype"
    tags = Tags()
    tags.feed(HTML)
    assert tags.tags, "index.html parsed to no tags"
    assert tags.tags[0][0] == "html", "the first tag in index.html must be <html>"
    return tags


def meta(name: str) -> str:
    assert name, "ask for a meta tag by its name or property"
    contents = [attrs.get("content", "") for tag, attrs in parsed().tags if tag == "meta" and name in (attrs.get("name"), attrs.get("property"))]
    assert len(contents) == 1, f"expected exactly one <meta> {name}, found {len(contents)}: add or dedupe it in the <head> of index.html"
    assert contents[0], f"<meta> {name} is empty: give it content"
    return contents[0]


def test_copy_has_no_em_or_en_dashes() -> None:
    found = [dash for dash in DASHES if dash in HTML]
    assert found == [], f"found {found}: rewrite with a comma, colon or full stop instead of a dash"


def test_copy_does_not_name_and_shame_libraries() -> None:
    text = " ".join(parsed().text).lower()
    named = [library for library in SHAMED_LIBRARIES if re.search(rf"\b{library}\b", text)]
    assert named == [], f"the copy names {named}: make the example about a pattern, not a library"


def test_cover_says_deterministic_rule_not_rules_md() -> None:
    lede = re.search(r'<p class="lede">(.*?)</p>', HTML, re.S)
    assert lede is not None, "the cover needs a <p class=\"lede\"> explaining the idea in one line"
    assert "deterministic rule" in lede.group(1), "the lede must say deterministic rule, so nobody reads rule as RULES.md"
    assert "RULES.md" in lede.group(1), "the lede must contrast a deterministic rule with a line in RULES.md"


def test_page_ships_no_javascript() -> None:
    scripts = [attrs for tag, attrs in parsed().tags if tag == "script"]
    handlers = [name for _, attrs in parsed().tags for name in attrs if name.startswith("on")]
    assert scripts == [], "found a <script>: do it in HTML and CSS, the page ships no JavaScript"
    assert handlers == [], f"found inline handlers {handlers}: the page ships no JavaScript"


def test_local_stylesheets_are_versioned() -> None:
    links = [attrs["href"] for tag, attrs in parsed().tags if tag == "link" and attrs.get("rel") == "stylesheet" and not attrs["href"].startswith("http")]
    assert links, "index.html links no local stylesheets"
    unversioned = [href for href in links if not re.search(r"\?v=\d+$", href)]
    assert unversioned == [], f"{unversioned} have no ?v=N: phones cache stylesheets for days, so version every local one"


def test_social_card_is_1200_by_630_and_linked() -> None:
    card = ROOT / "og.png"
    with card.open("rb") as image:
        header = image.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n", "og.png is not a PNG"
    width, height = struct.unpack(">II", header[16:24])
    assert (width, height) == (1200, 630), f"og.png is {width}x{height}: social cards need 1200x630"
    assert meta("og:image") == "https://exponentialengineering.dev/og.png", "og:image must be the absolute URL of og.png"
    assert meta("twitter:card") == "summary_large_image", "twitter:card must be summary_large_image to show the card"
    assert meta("og:title") and meta("og:description") and meta("description"), "titles and descriptions are what a shared link shows"


def test_in_page_links_point_at_real_ids() -> None:
    ids = {attrs["id"] for _, attrs in parsed().tags if "id" in attrs}
    anchors = {attrs["href"][1:] for tag, attrs in parsed().tags if tag == "a" and attrs.get("href", "").startswith("#")}
    assert anchors - ids == set(), f"links to missing ids {anchors - ids}: fix the href or the id"


def test_external_links_use_https() -> None:
    insecure = [attrs["href"] for tag, attrs in parsed().tags if tag == "a" and attrs.get("href", "").startswith("http://")]
    assert insecure == [], f"{insecure} use http: link the https version"


@pytest.mark.parametrize("width", WIDTHS)
def test_page_never_scrolls_sideways(page: Page, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(SITE.as_uri())
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    assert scroll_width == width, f"at {width}px the page is {scroll_width}px wide: something overflows sideways"


def test_everything_animated_in_ends_visible(page: Page) -> None:
    page.set_viewport_size({"width": 402, "height": 874})
    page.goto(SITE.as_uri())
    page.wait_for_timeout(COVER_ANIMATION_MS)
    height = page.evaluate("document.documentElement.scrollHeight")
    hidden: set[str] = set()
    for top in range(0, height, 300):
        page.evaluate(f"window.scrollTo(0, {top})")
        page.wait_for_timeout(100)
        hidden |= set(page.evaluate("""() => [...document.querySelectorAll('.page > *')]
            .filter((e) => { const r = e.getBoundingClientRect(); return r.top > 80 && r.bottom < 700 && parseFloat(getComputedStyle(e).opacity) < 0.5; })
            .map((e) => e.closest('.page').id)"""))
    assert hidden == set(), f"content in {sorted(hidden)} stays invisible after scrolling into view: check its animation-range"


def test_page_loads_without_console_errors(page: Page) -> None:
    errors: list[str] = []
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(SITE.as_uri())
    page.wait_for_timeout(500)
    assert errors == [], f"the browser reported {errors}"
