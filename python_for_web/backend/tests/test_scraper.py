import importlib.util
from pathlib import Path

import httpx
import pytest

MODULE = Path(__file__).resolve().parents[3] / "22_Day_Web_scraping" / "scraper.py"
spec = importlib.util.spec_from_file_location("scraper", MODULE)
scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper)


def test_fixture_and_metadata():
    html = (MODULE.parent / "fixtures/statistics.html").read_text()
    rows = scraper.parse_table(html, "https://example.org/stats", "2026-01-01T00:00:00Z")
    assert len(rows) == 4
    assert rows[0]["numeric_value"] == 1200
    assert [r["raw_value"] for r in rows[1:]] == ["70+", "10:1", "$5.4M"]
    assert all(r["numeric_value"] is None for r in rows[1:])
    assert rows[0]["source_url"] == "https://example.org/stats"


@pytest.mark.parametrize("html", ["<html></html>", "<table data-learning-stats></table>",
    "<table data-learning-stats><tbody><tr><td>Missing</td></tr></tbody></table>"])
def test_changed_markup(html):
    with pytest.raises(scraper.ExtractionError):
        scraper.parse_table(html, "fixture", "timestamp")


def test_fetch_timeout_and_robots(monkeypatch):
    real_client = httpx.Client

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /blocked")
        raise httpx.ReadTimeout("timeout", request=request)

    monkeypatch.setattr(scraper.httpx, "Client", lambda **kw: real_client(
        **kw, transport=httpx.MockTransport(handler)))
    with pytest.raises(ValueError, match="does not permit"):
        scraper.fetch_page("https://example.org/blocked")
    with pytest.raises(httpx.ReadTimeout):
        scraper.fetch_page("https://example.org/allowed")
