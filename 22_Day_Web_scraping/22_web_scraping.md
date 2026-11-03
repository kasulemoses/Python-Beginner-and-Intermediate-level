<div align="center">
  <h1> 30 Days Of Python: Day 22 - Web Scraping </h1>
  <a class="header-badge" target="_blank" href="https://www.linkedin.com/in/asabeneh/">
  <img src="https://img.shields.io/badge/style--5eba00.svg?label=LinkedIn&logo=linkedin&style=social">
  </a>
  <a class="header-badge" target="_blank" href="https://twitter.com/Asabeneh">
  <img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/asabeneh?style=social">
  </a>

<sub>Author:
<a href="https://www.linkedin.com/in/asabeneh/" target="_blank">Asabeneh Yetayeh</a><br>
<small> Second Edition: July, 2021</small>
</sub>
</div>

[<< Day 21](../21_Day_Classes_and_objects/21_classes_and_objects.md) | [Day 23 >>](../23_Day_Virtual_environment/23_virtual_environment.md)

![30DaysOfPython](../images/30DaysOfPython_banner3@2x.png)

- [📘 Day 22](#-day-22)
  - [Python Web Scraping](#python-web-scraping)
    - [What is web scraping?](#what-is-web-scraping)
  - [1. The tools we need](#1-the-tools-we-need)
  - [2. Understand the HTML first](#2-understand-the-html-first)
  - [3. Start with HTML we control](#3-start-with-html-we-control)
  - [4. Find elements](#4-find-elements)
  - [5. Extract text and links](#5-extract-text-and-links)
  - [6. Turn relative links into complete URLs](#6-turn-relative-links-into-complete-urls)
  - [7. Write a reusable extraction function](#7-write-a-reusable-extraction-function)
  - [8. Clean values without changing their meaning](#8-clean-values-without-changing-their-meaning)
  - [9. Save the results](#9-save-the-results)
  - [10. Download a real webpage](#10-download-a-real-webpage)
  - [11. Scrape more than one page](#11-scrape-more-than-one-page)
  - [12. Extract information from a table](#12-extract-information-from-a-table)
  - [13. Why some webpages need a different approach](#13-why-some-webpages-need-a-different-approach)
  - [14. Common problems](#14-common-problems)
  - [15. Exercises](#15-exercises)

# 📘 Day 22

## Python Web Scraping

### What is web scraping?

**Web scraping means using a program to collect information from webpages.**

For example, you might collect:

- Book titles and prices.
- Job titles and locations.
- News headlines and article links.
- Information from a table.

A scraper usually follows these steps:

**Get the webpage → Find the information → Extract it → Clean it → Save it**

In this lesson, we will begin with a small HTML example, then build a scraper for a practice website.

## 1. The tools we need

We will use two packages:

| Tool | Purpose |
| --- | --- |
| Requests | Downloads a webpage. |
| Beautiful Soup | Helps us find and extract information from its HTML. |

Install them:

```sh
python -m pip install requests beautifulsoup4
```

Import them:

```python
import requests
from bs4 import BeautifulSoup
```

The package is installed as `beautifulsoup4`, but we import it from `bs4`.

## 2. Understand the HTML first

HTML describes the structure of a webpage.

Consider this book:

```html
<article class="book">
    <h2>Learning Python</h2>
    <p class="price">£25.00</p>
    <a href="/books/learning-python">View book</a>
</article>
```

Here is what the parts mean:

| HTML | Meaning |
| --- | --- |
| `<article>` | Groups the information about one book. |
| `<h2>` | Contains the book title. |
| `<p>` | Contains a paragraph of text. |
| `class="price"` | Identifies an element using a class name. |
| `<a>` | Creates a link. |
| `href` | Stores the link's destination. |

**Before writing a scraper, identify the HTML elements containing the information you need.**

In a browser, right-click the information and select **Inspect** to examine its HTML.

## 3. Start with HTML we control

We can learn parsing without depending on an internet connection or a changing website.

The following examples use two fictional books. Run the short examples in the same Python file or session so they can share variables.

```python
from bs4 import BeautifulSoup

html = """
<html>
<head>
    <title>Our Bookshop</title>
</head>
<body>
    <h1 id="page-title">Available Books</h1>

    <article class="product_pod">
        <h3>
            <a href="books/learning-python.html"
               title="Learning Python">
                Learning Python
            </a>
        </h3>
        <p class="price_color">£25.00</p>
    </article>

    <article class="product_pod">
        <h3>
            <a href="books/understanding-classes.html"
               title="Understanding Classes">
                Understanding Classes
            </a>
        </h3>
        <p class="price_color">£18.50</p>
    </article>
</body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

print(soup.title.get_text())
```

**Output:**

```text
Our Bookshop
```

`BeautifulSoup` turns the HTML into a structure we can search. `"html.parser"` selects Python's built-in HTML parser.

## 4. Find elements

### Find one element

Use `find()` to get the first matching element:

```python
heading = soup.find("h1")

if heading is not None:
    print(heading.get_text(strip=True))
```

**Output:**

```text
Available Books
```

Find an element by its class:

```python
price = soup.find("p", class_="price_color")

if price is not None:
    print(price.get_text(strip=True))
```

**Output:**

```text
£25.00
```

We write `class_` because `class` already has a special meaning in Python.

### Find several elements

Use `find_all()` to get all matching elements:

```python
book_cards = soup.find_all("article", class_="product_pod")

print(len(book_cards))
```

**Output:**

```text
2
```

`find()` returns one element or `None`. `find_all()` returns a collection of matches, which can be empty.

### Find elements using CSS selectors

CSS selectors provide another way to describe the elements we want:

| Selector | What it selects |
| --- | --- |
| `h1` | All `<h1>` elements. |
| `.price_color` | Elements with class `price_color`. |
| `#page-title` | The element with ID `page-title`. |
| `article.product_pod` | Articles with class `product_pod`. |
| `h3 a` | Links inside `<h3>` elements. |

Use `select_one()` for the first match and `select()` for all matches:

```python
heading = soup.select_one("#page-title")
links = soup.select("article.product_pod h3 a")

if heading is not None:
    print(heading.get_text(strip=True))

for link in links:
    print(link.get("title"))
```

**Output:**

```text
Available Books
Learning Python
Understanding Classes
```

These searching methods are explained in the [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

## 5. Extract text and links

Text and HTML attributes are different things.

For example:

```html
<a href="books/learning-python.html" title="Learning Python">
    View book
</a>
```

- The visible text is `View book`.
- The `href` attribute contains the link.
- The `title` attribute contains `Learning Python`.

Using our bookshop HTML:

```python
link = soup.select_one("article.product_pod h3 a")

if link is not None:
    print(link.get_text(" ", strip=True))
    print(link.get("href"))
    print(link.get("title"))
```

**Output:**

```text
Learning Python
books/learning-python.html
Learning Python
```

`get_text(" ", strip=True)` removes surrounding whitespace and separates text fragments with spaces.

Using `.get("href")` returns `None` if the attribute is missing.

## 6. Turn relative links into complete URLs

A page may contain a link like:

```text
books/learning-python.html
```

This is a **relative URL**. It needs the page's URL to become a complete address.

Use `urljoin()`:

```python
from urllib.parse import urljoin

page_url = "https://example.com/"
relative_url = "books/learning-python.html"

full_url = urljoin(page_url, relative_url)

print(full_url)
```

**Output:**

```text
https://example.com/books/learning-python.html
```

Use the actual page URL as the base rather than joining strings manually. `urljoin()` understands paths such as `../` and `/books/`. [Python's URL documentation](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)

This operation builds an address; it does not visit it.

## 7. Write a reusable extraction function

Rather than repeating our extraction code, put it in a function.

Save this code in **`book_parser.py`**:

```python
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def extract_books(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.product_pod")

    if not cards:
        raise ValueError(
            "No book cards found. Check the page and selectors."
        )

    books = []

    for card in cards:
        link = card.select_one("h3 a")
        price_tag = card.select_one(".price_color")

        if link is None:
            raise ValueError("A book is missing its title link.")

        href = link.get("href")

        if not href:
            raise ValueError("A book link is missing its destination.")

        title = link.get("title") or link.get_text(" ", strip=True)
        title = title.strip()

        if not title:
            raise ValueError("A book title is empty.")

        price = (
            price_tag.get_text(" ", strip=True)
            if price_tag is not None
            else None
        )

        books.append({
            "title": title,
            "price": price,
            "url": urljoin(page_url, href),
        })

    return books
```

Now use it with our sample HTML:

```python
from book_parser import extract_books

books = extract_books(html, "https://example.com/")

for book in books:
    print(book["title"], "-", book["price"])
```

**Output:**

```text
Learning Python - £25.00
Understanding Classes - £18.50
```

Notice our decisions:

- A missing required title or link produces a clear error.
- A missing optional price becomes `None`.
- We extract information from each book card separately.

**Keeping each book's information together prevents us from accidentally pairing one book's title with another book's price.**

A missing price does not mean the book is free, so we should not replace it with `0`.

## 8. Clean values without changing their meaning

Scraped data often contains spaces, currency symbols, or number separators.

For a price in a known format:

```python
from decimal import Decimal

raw_price = "£1,200.50"

amount = Decimal(
    raw_price.removeprefix("£").replace(",", "")
)

print(amount)
```

**Output:**

```text
1200.50
```

`Decimal` is useful when we want exact decimal values.

However, do not remove characters blindly:

| Original value | Meaning |
| --- | --- |
| `70+` | At least 70. |
| `10:1` | A ratio. |
| `25%` | A percentage. |
| `£25.00` | An amount in a particular currency. |

Keep the original value if you are unsure how to interpret it. Our book parser preserves prices as strings.

## 9. Save the results

### Save as JSON

JSON works well with Python lists and dictionaries.

Continue with the `books` variable from our sample:

```python
import json

with open("books.json", "w", encoding="utf-8") as file:
    json.dump(
        books,
        file,
        ensure_ascii=False,
        indent=2,
    )

print("Saved books.json")
```

The file will contain records like:

```json
[
  {
    "title": "Learning Python",
    "price": "£25.00",
    "url": "https://example.com/books/learning-python.html"
  }
]
```

This shows one record; our sample contains two.

`ensure_ascii=False` keeps characters such as `£` readable. Python's `None` is written as JSON `null`.

### Save as CSV

CSV is useful when you want to open the data in a spreadsheet.

```python
import csv

with open(
    "books.csv",
    "w",
    newline="",
    encoding="utf-8",
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["title", "price", "url"],
    )

    writer.writeheader()
    writer.writerows(books)

print("Saved books.csv")
```

`DictWriter` writes dictionary values into named columns. `newline=""` lets the CSV module handle line endings correctly. [Python's CSV documentation](https://docs.python.org/3/library/csv.html#csv.DictWriter)

These examples overwrite the output file each time. Appending requires a separate plan for headers and duplicates.

## 10. Download a real webpage

Before collecting data from a website:

- Check its terms and scraping instructions.
- Check its `robots.txt` rules.
- Prefer an official API when one is available and suitable.
- Collect only what you need.
- Avoid rapid repeated requests.
- Do not bypass login requirements or access restrictions.

`robots.txt` describes crawler rules. It is not a password system or a replacement for permission. Python provides [`urllib.robotparser`](https://docs.python.org/3/library/urllib.robotparser.html) for reading those rules programmatically.

For practice, we will use [Books to Scrape](https://books.toscrape.com/), which identifies itself as a web-scraping demo. Its prices and ratings are fictional.

```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/"

response = requests.get(
    url,
    timeout=(5, 15),
    headers={"User-Agent": "PythonLearningScraper/1.0"},
)

response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

if soup.title is not None:
    print(soup.title.get_text(strip=True))
```

Here:

- `requests.get()` downloads the page.
- `timeout=(5, 15)` sets connection and read timeouts.
- `raise_for_status()` raises an error for unsuccessful HTTP statuses.
- `response.content` contains the response bytes.
- Beautiful Soup parses those bytes as HTML.

A Requests timeout limits waiting during connection or reading; it is not a guaranteed total runtime limit. [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)

### Handle request failures

A request can fail because of a timeout, connection problem, or HTTP error.

```python
import requests

try:
    response = requests.get(
        "https://books.toscrape.com/",
        timeout=(5, 15),
    )
    response.raise_for_status()

except requests.Timeout:
    print("The website took too long to respond.")

except requests.HTTPError as error:
    print("The website returned an HTTP error:", error)

except requests.RequestException as error:
    print("Could not download the page:", error)

else:
    print("Page downloaded successfully.")
```

Check the response before parsing it. An error page is still HTML, but it is not the information we wanted.

## 11. Scrape more than one page

**Pagination means splitting results across several pages.**

A page may have a **Next** link:

```html
<li class="next">
    <a href="page-2.html">Next</a>
</li>
```

The basic idea is:

1. Download the current page.
2. Extract its records.
3. Find the next-page link.
4. Resolve the link using the current page URL.
5. Continue until there is no next link or we reach our limit.

We should also prevent repeated visits and remove duplicate records.

### Complete example: collect up to three pages

Keep `book_parser.py` from Section 7 in the same folder.

Save the following as **`scrape_books.py`**:

```python
import json
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from book_parser import extract_books


def scrape_books(start_url, max_pages=3):
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1.")

    url = start_url
    visited = set()
    books_by_url = {}

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "PythonLearningScraper/1.0"
        })

        for page_number in range(max_pages):
            if url in visited:
                raise ValueError("The next link repeats an earlier page.")

            visited.add(url)

            if page_number > 0:
                time.sleep(1)

            response = session.get(url, timeout=(5, 15))
            response.raise_for_status()

            page_url = response.url

            books = extract_books(
                response.content,
                page_url,
            )

            for book in books:
                books_by_url[book["url"]] = book

            soup = BeautifulSoup(
                response.content,
                "html.parser",
            )

            next_link = soup.select_one("li.next a")

            if next_link is None:
                break

            href = next_link.get("href")

            if not href:
                raise ValueError("The next link has no destination.")

            next_url = urljoin(page_url, href)

            if urlparse(next_url).netloc != urlparse(start_url).netloc:
                raise ValueError("The next link leaves the practice site.")

            url = next_url

    return list(books_by_url.values())


def main():
    books = scrape_books(
        "https://books.toscrape.com/",
        max_pages=3,
    )

    with open("books.json", "w", encoding="utf-8") as file:
        json.dump(
            books,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved {len(books)} books to books.json")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError, OSError) as error:
        print("Scraping failed:", error)
```

Run it:

```sh
python scrape_books.py
```

This example:

- Reuses a session for several requests.
- Limits the number of pages.
- Pauses between page requests.
- Detects repeated page links.
- Removes duplicate books using their URLs.
- Reports failures instead of silently saving incomplete results.

A session can reuse connections and shared settings across requests. [Requests session documentation](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects)

The one-second pause is only a teaching example. Follow each website's actual limits. If a server returns `429 Too Many Requests`, stop and follow its retry instructions rather than repeatedly sending requests.

## 12. Extract information from a table

Tables use rows and cells:

- `<tr>`: a row.
- `<th>`: a heading cell.
- `<td>`: a data cell.

Here is a complete example:

```python
from bs4 import BeautifulSoup

html = """
<table id="students">
    <thead>
        <tr>
            <th>Name</th>
            <th>Country</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Moses</td>
            <td>Uganda</td>
        </tr>
        <tr>
            <td>Amina</td>
            <td>Kenya</td>
        </tr>
    </tbody>
</table>
"""

soup = BeautifulSoup(html, "html.parser")
table = soup.select_one("#students")

if table is None:
    raise ValueError("Student table not found.")

students = []

for row in table.select("tbody tr"):
    cells = row.find_all("td", recursive=False)

    if len(cells) != 2:
        raise ValueError("Expected two cells in each row.")

    students.append({
        "name": cells[0].get_text(" ", strip=True),
        "country": cells[1].get_text(" ", strip=True),
    })

for student in students:
    print(student["name"], "-", student["country"])
```

**Output:**

```text
Moses - Uganda
Amina - Kenya
```

This handles a simple table. Tables with merged cells, nested tables, `rowspan`, or `colspan` need additional logic.

## 13. Why some webpages need a different approach

### Static content

The information is already in the HTML returned by the server.

Requests and Beautiful Soup are often enough.

### JavaScript-generated content

The browser downloads the initial page, then JavaScript adds information afterward.

Requests does not run JavaScript. Beautiful Soup only parses the HTML supplied to it.

If information appears in your browser but not in the downloaded HTML:

1. Check whether the website provides an official API.
2. Examine the browser's Network panel to understand how the page loads.
3. Consider browser automation as a later topic if rendering is necessary and permitted.

Do not assume an empty result means there is no information on the website.

## 14. Common problems

| Problem | What to check |
| --- | --- |
| `NoneType` error | Did your selector find an element before you used it? |
| Empty list | Is the selector correct? Is the information in the downloaded HTML? |
| Garbled characters | Check the page encoding; inspect the original response bytes. |
| Wrong title paired with a price | Extract related fields inside the same book card. |
| Duplicate records | Use a suitable identifier, such as the book URL. |
| Relative links do not work | Resolve them with `urljoin()`. |
| Scraper suddenly stops working | The website's HTML may have changed. |
| `403` or `429` response | Review access rules and request limits; do not try to bypass them. |

## 15. Exercises

### Level 1 — Find and extract

1. Extract the heading from the sample bookshop HTML.
2. Print the title and link for each book.
3. Count the book cards.
4. Add a third fictional book and run the examples again.

### Level 2 — Handle and save data

1. Remove one book's price. Confirm that its price becomes `None`.
2. Remove a required title link. Confirm that the parser reports a clear error.
3. Save the fictional books as JSON and CSV.
4. Add an availability field, such as `"In stock"`.
5. Add a third student row to the table example and extract it.

### Level 3 — Build a small scraper

1. Run the practice scraper with `max_pages=1`, then `max_pages=2`.
2. Explain why the next-page link must use the current page URL as its base.
3. Explain how the dictionary removes duplicate book URLs.
4. Add a source-page URL and a UTC collection timestamp to each record.
5. Save a downloaded page locally, then parse that saved copy without downloading it again.
6. Adapt the table parser to another permitted page after inspecting its current HTML.

**By the end of Day 22, you should be able to download a page, locate information, extract structured records, handle common failures, follow pagination, and save useful results.**

[<< Day 21](../21_Day_Classes_and_objects/21_classes_and_objects.md) | [Day 23 >>](../23_Day_Virtual_environment/23_virtual_environment.md)
