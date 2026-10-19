from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

SITE = Path(__file__).parent.parent / "index.html"


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("width", [1100, 402])
def test_page_has_no_accessibility_findings(page: Page, scheme: str, width: int) -> None:
    page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(SITE.as_uri())
    results = Axe().run(page, options={})
    findings = results.response["violations"] + results.response["incomplete"]
    assert findings == [], results.generate_report()
