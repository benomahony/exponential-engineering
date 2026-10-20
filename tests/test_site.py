import hashlib
import re
import struct
from html.parser import HTMLParser
from pathlib import Path

import pytest
from playwright.sync_api import Page

ROOT = Path(__file__).parent.parent
SITE = ROOT / "index.html"
HTML = SITE.read_text()
STYLESHEETS = {path.name: path.read_bytes() for path in ROOT.glob("*.css")}
TEST_NAMES = {name for path in (ROOT / "tests").glob("test_*.py") for name in re.findall(r"^def (test_\w+)", path.read_text(), re.M)}
SHAMED_LIBRARIES = ["pandas", "requests", "numpy", "django", "flask", "jquery"]
DASHES = ["—", "–"]
WIDTHS = [320, 402, 768, 1100, 1440]
CODE_TAGS = {"pre", "code"}
SHAMING_PHRASES = ["banned", "is bad", "never use", "don't use"]
COVER_ANIMATION_MS = 4000
MINIMUM_CONTRAST = 4.5


class Tags(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text: list[str] = []
        self.prose: list[str] = []
        self.code_depth = 0
        assert self.tags == [], "a new parser starts with no tags"
        assert self.text == [], "a new parser starts with no text"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        assert tag, "the parser only reports start tags that have a name"
        count = len(self.tags)
        self.tags.append((tag, {name: value or "" for name, value in attrs}))
        self.code_depth += tag in CODE_TAGS
        assert len(self.tags) == count + 1, "each start tag is recorded exactly once"

    def handle_endtag(self, tag: str) -> None:
        assert tag, "the parser only reports end tags that have a name"
        self.code_depth -= tag in CODE_TAGS
        assert self.code_depth >= 0, f"</{tag}> closes a code block that never opened"

    def handle_data(self, data: str) -> None:
        assert self.rawdata, "text only arrives while a document is being fed"
        count = len(self.text)
        self.text.append(data)
        if self.code_depth == 0:
            self.prose.append(data)
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


def test_copy_does_not_ban_things() -> None:
    prose = " ".join(parsed().prose).lower()
    shaming = [phrase for phrase in SHAMING_PHRASES if phrase in prose]
    assert shaming == [], f"the copy says {shaming}: point people at the better pattern instead of banning something by name"


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


def test_local_stylesheets_are_versioned_by_their_content() -> None:
    links = [attrs["href"] for tag, attrs in parsed().tags if tag == "link" and attrs.get("rel") == "stylesheet" and not attrs["href"].startswith("http")]
    assert links, "index.html links no local stylesheets"
    expected = {name: hashlib.sha256(content).hexdigest()[:8] for name, content in STYLESHEETS.items()}
    assert {href.split("?")[0] for href in links} == set(expected), f"index.html should link exactly {sorted(expected)}"
    stale = [f"{href} should end ?v={expected[href.split('?')[0]]}" for href in links if href != f"{href.split('?')[0]}?v={expected[href.split('?')[0]]}"]
    assert stale == [], f"phones cache stylesheets for days, so each link carries the first 8 characters of its file's sha256: {stale}"


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


def channels(colour: str) -> tuple[float, float, float]:
    colour = colour.strip()
    assert colour.startswith(("#", "rgb")), f"cannot read colour {colour!r}: use hex or rgb()"
    if colour.startswith("#"):
        values = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    else:
        values = [int(float(part)) for part in re.findall(r"[\d.]+", colour)[:3]]
    assert all(0 <= value <= 255 for value in values), f"{colour} has a channel outside 0 to 255"
    return (values[0] / 255, values[1] / 255, values[2] / 255)


def luminance(colour: str) -> float:
    assert colour.strip(), "luminance needs a colour"
    linear = [part / 12.92 if part <= 0.03928 else ((part + 0.055) / 1.055) ** 2.4 for part in channels(colour)]
    result = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    assert 0 <= result <= 1, f"luminance of {colour} came out as {result}"
    return result


def contrast(foreground: str, background: str) -> float:
    assert foreground.strip() and background.strip(), "contrast needs both a foreground and a background colour"
    lighter, darker = sorted([luminance(foreground), luminance(background)], reverse=True)
    ratio = (lighter + 0.05) / (darker + 0.05)
    assert 1 <= ratio <= 21, f"contrast of {foreground} on {background} came out as {ratio}"
    return ratio


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_highlighted_text_reads_on_its_band_and_on_the_paper(page: Page, scheme: str) -> None:
    page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
    page.goto(SITE.as_uri())
    highlights = page.evaluate("""() => [...document.querySelectorAll('.hl')].map((e) => {
        const style = getComputedStyle(e);
        const solid = style.backgroundColor !== 'rgba(0, 0, 0, 0)';
        return [e.textContent.trim(), style.color, style.getPropertyValue('--hl'), solid ? null : style.getPropertyValue('--paper')];
    })""")
    assert highlights, "the page has no .hl highlights to check"
    failures = [
        f"{text!r}: {ratio:.2f} on {name}"
        for text, ink, band, paper in highlights
        for name, background in (("its band", band), ("the paper", paper))
        if background is not None and (ratio := contrast(ink, background)) < MINIMUM_CONTRAST
    ]
    assert failures == [], f"highlighted text below {MINIMUM_CONTRAST}:1 in {scheme} mode: {failures}"


OVERLAPPING_HIGHLIGHTS = """() => {
    const textRects = (root) => {
        const rects = [];
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            if (!walker.currentNode.textContent.trim()) continue;
            const range = document.createRange();
            range.selectNodeContents(walker.currentNode);
            rects.push(...range.getClientRects());
        }
        return rects;
    };
    for (const card of document.querySelectorAll('.page')) card.style.transform = 'none';
    const overlaps = [];
    for (const highlight of document.querySelectorAll('.hl')) {
        const block = highlight.closest('h1, h2, h3, p, li, td, th');
        for (const band of highlight.getClientRects()) {
            const middle = band.top + band.height / 2;
            for (const text of textRects(block)) {
                const otherLine = text.bottom < middle || text.top > middle;
                const height = Math.min(band.bottom, text.bottom) - Math.max(band.top, text.top);
                const width = Math.min(band.right, text.right) - Math.max(band.left, text.left);
                if (otherLine && height > 0.5 && width > 0.5) overlaps.push(`${highlight.textContent.trim()} by ${height.toFixed(1)}px`);
            }
        }
    }
    return [...new Set(overlaps)];
}"""


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("width", WIDTHS)
def test_highlights_never_cover_a_neighbouring_line(page: Page, scheme: str, width: int) -> None:
    page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(SITE.as_uri())
    page.evaluate("document.fonts.ready.then(() => true)")
    overlaps = page.evaluate(OVERLAPPING_HIGHLIGHTS)
    assert overlaps == [], f"at {width}px in {scheme} mode these highlights paint over the line above or below: {overlaps}. Give the block a line-height at least as tall as its font's glyph box"


FINISHED_CURVE = "M10 108 C110 106 150 90 188 12"


def test_reduced_motion_shows_the_finished_cover_curve_without_animating(page: Page) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.goto(SITE.as_uri())
    visible = page.evaluate("""() => [...document.querySelectorAll('.cover .expo')]
        .filter((path) => getComputedStyle(path).display !== 'none')
        .map((path) => [path.getAttribute('d'), path.querySelectorAll('animate').length])""")
    assert len(visible) == 1, f"with reduced motion the cover should show exactly one curve, found {len(visible)}"
    assert visible[0] == [FINISHED_CURVE, 0], f"with reduced motion the cover curve should be the finished one with no animation, found {visible[0]}"


@pytest.mark.parametrize("width", WIDTHS)
def test_every_card_grows_to_fit_its_content(page: Page, width: int) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(SITE.as_uri())
    page.evaluate("document.fonts.ready.then(() => true)")
    overflowing = page.evaluate("""() => [...document.querySelectorAll('.page')]
        .filter((card) => card.scrollHeight > card.clientHeight + 1)
        .map((card) => `${card.id} needs ${card.scrollHeight}px but has ${card.clientHeight}px`)""")
    assert overflowing == [], f"at {width}px these cards spill into the next one: {overflowing}. Let the card grow instead of fixing its height"


def test_the_rules_on_this_page_match_the_test_suite() -> None:
    listed = {attrs["data-test"] for _, attrs in parsed().tags if "data-test" in attrs}
    assert listed, "the practice what we preach card lists no rules: give each <li> a data-test naming its test"
    assert listed == TEST_NAMES, f"missing from the page: {sorted(TEST_NAMES - listed)}; listed but no such test: {sorted(listed - TEST_NAMES)}"
