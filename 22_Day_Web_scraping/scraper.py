"""Day 22: deterministic table extraction, with an optional explicit live fetch."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "PythonLearningScraper/1.0 (educational; single-page request)"


class ExtractionError(ValueError):
    pass


def parse_table(html: str, source_url: str, fetched_at: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table[data-learning-stats]")
    if table is None:
        raise ExtractionError("Expected table[data-learning-stats]; the page structure may have changed")
    records = {}
    for row in table.select("tbody tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) != 3:
            raise ExtractionError("Expected category, metric, and value in every row")
        category, metric, raw = [cell.get_text(" ", strip=True) for cell in cells]
        if not all((category, metric, raw)):
            raise ExtractionError("Table cells cannot be empty")
        key = (category, metric)
        record = {"schema_version": 1, "source_url": source_url, "fetched_at": fetched_at,
                  "category": category, "metric": metric, "raw_value": raw}
        # Only plain non-negative integers are normalized automatically.
        # Money, ratios, ranges, and lower bounds preserve their original meaning.
        compact = raw.replace(",", "")
        record["numeric_value"] = int(compact) if compact.isascii() and compact.isdigit() else None
        if key in records and records[key]["raw_value"] != raw:
            raise ExtractionError("Conflicting duplicate metric: " + metric)
        records[key] = record
    if not records:
        raise ExtractionError("The statistics table has no data rows")
    return list(records.values())


def fetch_page(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public HTTPS URL without embedded credentials")
    # This CLI is for trusted, learner-chosen sources, not an arbitrary-URL API.
    with httpx.Client(timeout=10, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        robots_response = client.get(robots_url)
        if robots_response.status_code != 404:
            robots_response.raise_for_status()
            rules = RobotFileParser()
            rules.parse(robots_response.text.splitlines())
            if not rules.can_fetch(USER_AGENT, url):
                raise ValueError("robots.txt does not permit this fetch")
        response = client.get(url)
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", ""):
            raise ValueError("Expected an HTML response")
        return response.text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--html", type=Path, help="Saved HTML fixture; works offline")
    source.add_argument("--url", help="Trusted HTTPS page, after checking its terms and permission")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        html = args.html.read_text(encoding="utf-8") if args.html else fetch_page(args.url)
        source_url = args.html.resolve().as_uri() if args.html else args.url
        rows = parse_table(html, source_url, datetime.now(timezone.utc).isoformat())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, httpx.HTTPError) as exc:
        parser.exit(1, f"Scraping failed: {exc}\n")
    print(f"Exported {len(rows)} records to {args.output}")


if __name__ == "__main__":
    main()
