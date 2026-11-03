# Day 22 — Reliable web scraping

Based on the original 30 Days of Python material by Asabeneh Yetayeh. Modernized with an offline-first, reproducible exercise.

[← Day 21](../21_Day_Classes_and_objects/21_classes_and_objects.md) | [Day 23 →](../23_Day_Virtual_environment/23_virtual_environment.md)

## What you will learn

Fetch HTML, select elements, validate a table, clean values without losing meaning, and export JSON with source metadata.

Prerequisites: functions, dictionaries, exceptions, file handling, and basic HTML. Install the shared Python dependencies using the [application setup](../python_for_web/README.md).

## Start offline

The fixture contains fictional statistics. It is stable, needs no website account, and makes tests reproducible.

From the repository root:

```sh
python_for_web/backend/.venv/bin/python 22_Day_Web_scraping/scraper.py \
  --html 22_Day_Web_scraping/fixtures/statistics.html \
  --output /tmp/python-learning-statistics.json
```

Windows: use `python_for_web/backend/.venv/Scripts/python.exe`.

Expected result: four records exported. The first metric, Students, has raw value `1,200` and numeric value `1200`. Programs (`70+`), ratio (`10:1`), and awards (`$5.4M`) retain their raw values and have no automatic numeric conversion.

## Understand the parser

Beautiful Soup turns HTML into a searchable tree:

```py
from bs4 import BeautifulSoup

html = '<table data-learning-stats><tbody><tr><td>Community</td><td>Students</td><td>1,200</td></tr></tbody></table>'
soup = BeautifulSoup(html, "html.parser")
table = soup.select_one("table[data-learning-stats]")
if table is None:
    raise ValueError("Statistics table is missing")
for row in table.select("tbody tr"):
    values = [cell.get_text(" ", strip=True) for cell in row.find_all("td", recursive=False)]
    print(values)
```

Read [scraper.py](scraper.py). It separates `fetch_page`, `parse_table`, and command-line export. The parser validates three nonempty columns, rejects missing tables and conflicting duplicate metrics, and removes identical duplicate rows.

Each record includes:
- `schema_version`: the output shape's version.
- `source_url`: fixture file URI or the live page URL.
- `fetched_at`: UTC timestamp.
- `category`, `metric`, `raw_value`, and optional `numeric_value`.

A lower bound, ratio, currency, percentage, or measurement needs explicit interpretation. Removing every non-digit character produces incorrect data.

## Fetching live websites

Check site terms, permission, and robots.txt before collecting data. Use a public HTTPS source you trust. The optional `--url` mode fetches robots.txt and one page with a ten-second timeout and an identifying user agent. It refuses redirects and disallowed paths and reports HTTP or extraction failures. A missing robots.txt (404) is allowed; other HTTP errors fail the fetch.

This parser expects our teaching table. A third-party website requires its own inspected selector and saved fixture; the old UCI/Boston University examples are not promised to match this schema. Some pages render data through JavaScript or provide an official API, which may be more appropriate.

Do not run rapid repeated requests. For a larger collector, add source-specific pacing, caching, response-size bounds, and bounded retries that respect server instructions. This exercise does not expose arbitrary URL fetching through the API.

The existing `scrapped_data.json` remains a historical sample with unknown collection time. Do not treat it as current institutional data.

## Exercises

1. Run the fixture exporter and inspect all four records.
2. Remove the table attribute in a copy of the fixture. Confirm a clear error and a nonzero exit status.
3. Duplicate a row, then change the duplicate's value. Compare deduplication with conflict detection.
4. Add an explicit representation for percentages without changing the raw value.
5. Save another permitted HTML table, adapt a separate parser, and add its fixture and expected output.

Run the scraping tests from `python_for_web/backend`:

```sh
.venv/bin/python -m pytest tests/test_scraper.py -q
```

**You are finished when:** export works offline, output preserves meaning, and missing elements and network failures are tested.

References: [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/).

[← Day 21](../21_Day_Classes_and_objects/21_classes_and_objects.md) | [Day 23 →](../23_Day_Virtual_environment/23_virtual_environment.md)
