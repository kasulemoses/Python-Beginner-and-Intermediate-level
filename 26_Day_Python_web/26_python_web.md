# Day 26 — Python for the web with FastAPI

Based on the original 30 Days of Python material by Asabeneh Yetayeh. The Flask/Jinja example has been replaced by a working FastAPI API and Next.js frontend.

[← Day 25](../25_Day_Pandas/25_pandas.md) | [Day 27 →](../27_Day_Python_with_mongodb/27_python_with_mongodb.md)

## Learning goals

Separate business logic, API validation, and presentation. Build a complete text analyzer rather than a form that only redirects.

Prerequisites: Python functions, dictionaries, exceptions, type hints; introductory HTML and JavaScript. For the frontend, study React components, props, state, and form events. Next.js uses React; Tailwind supplies CSS utilities, while semantic HTML remains necessary.

## Run the application

Follow the [shared setup guide](../python_for_web/README.md). Text analysis does not require a database.

- FastAPI: http://127.0.0.1:8000/docs
- Next.js: http://localhost:3000
- Analyzer: http://localhost:3000/analyzer

## Folder responsibilities

```text
python_for_web/
  backend/
    app/main.py          # HTTP routes and lifecycle
    app/schemas.py       # typed inputs and outputs
    app/analysis.py      # pure text analysis
    app/students.py      # database operations
    tests/
  frontend/
    app/layout.tsx       # shared navigation and page layout
    app/analyzer/page.tsx
    app/students/page.tsx
    app/globals.css      # Tailwind import and shared utility compositions
    lib/api.ts           # JSON requests and readable errors
```

## Define behavior first

The analyzer accepts 1–50,000 Unicode code points and rejects whitespace-only input. Its character count includes original spaces and punctuation.

Words are Unicode letters/digits, separated by punctuation, whitespace, or underscores. Internal straight/curly apostrophes stay in a word; curly apostrophes are normalized to straight ones. Words are NFC-normalized and case-folded before counting. Emoji and punctuation by themselves are not words. Hyphenated words become separate words.

Return total words, unique words, and up to ten frequent words, ordered by descending frequency and then alphabetically for ties. Text is not stored.

For `Python python learning`, expect 22 characters, 3 words, 2 unique words, and frequencies `python: 2`, `learning: 1`.

## Pure Python before HTTP

From `python_for_web/backend`:

```py
from app.analysis import analyze

result = analyze("Python python learning")
print(result.model_dump())
```

This function can be tested without a browser, server, or database.

## FastAPI request validation

The real route uses these imported schemas:

```py
from fastapi import FastAPI
from app.analysis import analyze
from app.schemas import AnalysisRequest, AnalysisResult

app = FastAPI()

@app.post("/api/v1/analysis", response_model=AnalysisResult)
def analysis(payload: AnalysisRequest):
    return analyze(payload.text)
```

Use the actual application's startup command from the setup guide; this short snippet only demonstrates how the pieces fit together. Pydantic checks input fields and FastAPI exposes the contract in OpenAPI.

```sh
curl -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H 'Content-Type: application/json' \
  -d '{"text":"Python python learning"}'
```

## React and Tailwind

The analyzer page is a client component because it uses form events and state. Home/about pages can remain server components. The form posts JSON to the same-origin `/api/v1/analysis` path. Next.js forwards it to the server-only `API_ORIGIN` setting.

A Tailwind-styled button still uses semantic HTML:

```tsx
<button type="submit" className="rounded-xl bg-teal-800 px-5 py-3 font-semibold text-white">
  Analyze text
</button>
```

Read the actual analyzer page to study a labeled textarea, disabled submit state, loading feedback, results, and errors that preserve input. Never inject submitted text as HTML.

## Production basics

Use a production ASGI server command for FastAPI and a production Next.js build. Disable development reload in production. Keep environment secrets outside source control. The setup guide includes exact commands and health checks.

The previous free-Heroku instructions are retired; [Heroku ended free dynos in 2022](https://devcenter.heroku.com/changelog-items/2502). Verify current hosting terms when selecting a provider.

## Exercises

1. Verify the example counts through Python, Swagger UI, and the browser.
2. Try spaces, punctuation-only text, apostrophes, accented words, and emoji. Explain the differences between words and characters.
3. Stop the API and submit text. Confirm an error appears without losing the input.
4. Change the maximum frequency list length and update its tests.
5. Check keyboard navigation and a narrow phone-sized viewport.

**You are finished when:** real results appear, invalid input is rejected, and the API and frontend build/tests pass.

References: [FastAPI](https://fastapi.tiangolo.com/tutorial/), [React](https://react.dev/learn), [Next.js](https://nextjs.org/docs/app), [Tailwind with Next.js](https://tailwindcss.com/docs/installation/framework-guides/nextjs).

[← Day 25](../25_Day_Pandas/25_pandas.md) | [Day 27 →](../27_Day_Python_with_mongodb/27_python_with_mongodb.md)
