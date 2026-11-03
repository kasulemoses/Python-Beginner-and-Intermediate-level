# Python Learning Lab

A working companion to Days 22 and 26–29: offline web scraping, text analysis, MongoDB, HTTP, and student CRUD.

## Stack

- Python 3.13 recommended; FastAPI, Pydantic, PyMongo Async.
- Node.js 20.9+ (Node 24 used for verification); Next.js App Router, React, TypeScript, Tailwind 4.
- MongoDB 8 for student storage. Text analysis works without it.

The numbered lesson folders explain the implementation. This directory contains the shared runnable application.

## Backend setup

From this directory:

```sh
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Windows: create the environment with `py -3.13 -m venv .venv`, activate `.venv\Scripts\Activate.ps1`, and copy the example environment file using your shell.

Open http://127.0.0.1:8000/docs for interactive API documentation.

requirements.lock records the exact dependencies used for verification, including tests. pyproject.toml declares direct dependencies and compatible ranges for deliberate future updates. To regenerate the lock, install the declared dependencies and test tools into a clean environment, run the checks, then freeze it.

## MongoDB

Use a local MongoDB server or an Atlas database you control. Start your database according to its official installation guide, then set the backend .env:

```dotenv
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=python_learning
CORS_ORIGINS=["http://localhost:3000"]
```

For Atlas, use its supplied connection string, a restricted database user, and appropriate network access. Never commit credentials.

From backend, with the environment activated:

```sh
python -m app.seed
```

This explicitly ensures two fictional learner records using reserved IDs and preserves subsequent edits. It is safe to rerun and does not delete data. Reload/restart does not seed automatically. No database content from an existing deployment is migrated automatically.

If you only want the analyzer, leave MONGODB_URI unset. If configured storage is unreachable at startup, analysis remains available but student routes return 503; restart the API after restoring storage.

## Frontend setup

In a second terminal, from this directory:

```sh
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. The analyzer is at /analyzer and the student directory at /students.

The browser calls /api/v1 on the frontend origin. Next.js forwards those requests to API_ORIGIN (default http://127.0.0.1:8000). Set API_ORIGIN to the backend's internal origin before building for deployment. It is server-only; no NEXT_PUBLIC database setting is needed.

If connecting a browser directly to a different API origin, configure an explicit backend CORS_ORIGINS array. CORS is not authentication.

## Behavior

### Analyzer

POST /api/v1/analysis accepts {"text":"..."} and returns character_count, word_count, unique_word_count, and up to ten frequent_words.

Input is limited to 50,000 Python Unicode code points and must not be blank. Character count preserves original whitespace and punctuation. Words use NFC normalization, case folding, and apostrophe normalization; digits count as words, underscores and hyphens separate them. Frequency ties sort alphabetically. Emoji/punctuation alone produce zero words. Analysis is not saved.

The browser's textarea limit is conservative for astral Unicode characters because HTML maxLength uses UTF-16 units. The API's reported count uses Python code points, not visual grapheme clusters.

### Students

Fields: name, country, city, date_of_birth (ISO date), skills (array), bio. The server supplies id, created_at, and updated_at. Future birthdays, blank required fields, null values, and unknown input fields are rejected.

| Method | URL | Result |
| --- | --- | --- |
| GET | /api/v1/students?country=Uganda&offset=0&limit=10 | items, total, offset, limit |
| POST | /api/v1/students | 201, new student and Location |
| GET | /api/v1/students/{id} | one object or 404 |
| PATCH | /api/v1/students/{id} | partial update, preserving created_at |
| DELETE | /api/v1/students/{id} | 204, no body |

Lists sort by name and id; country is an exact match. limit is 1–100; offset is 0–100,000. Concurrent writes may shift offset pages. Malformed IDs return 422; valid absent IDs return 404. Storage failures return safe 503 messages.

No PUT/full replacement endpoint is provided.

## Checks

From backend:

```sh
python -m pytest -q
```

Without a database URI, the real MongoDB cases are explicitly skipped; other tests still run. To exercise real persistence, point to a dedicated local test server:

```sh
MONGODB_TEST_URI=mongodb://127.0.0.1:27017 python -m pytest -q
```

Integration tests create random python_learning_test_* databases and delete only those test databases afterward. The test account must have permission to create and drop those disposable databases. Never point testing at a production server.

From frontend:

```sh
npm run typecheck
npm run build
npx playwright install chromium
npm test
```

Browser tests require both servers running at 127.0.0.1:8000 and 127.0.0.1:3000 with MongoDB configured. Use a separate disposable database for that API. Tests create fictional records and delete the records they created. They cover desktop/mobile analysis, student CRUD, and preserved input after errors.

CI performs backend checks with MongoDB, builds the frontend, starts both servers, and runs browser tests.

## Day 22 scraper

From the repository root:

```sh
python_for_web/backend/.venv/bin/python 22_Day_Web_scraping/scraper.py \
  --html 22_Day_Web_scraping/fixtures/statistics.html \
  --output /tmp/python-learning-statistics.json
```

See [Day 22](../22_Day_Web_scraping/22_web_scraping.md) for extraction behavior and live-source restrictions. Existing scrapped_data.json is a historical sample, not current institutional data.

## Production preparation

Keep this learning app local with fictional records until authentication and authorization are added for public student writes. There are no user accounts or access rules in this milestone.

Backend, from backend:

```sh
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend, from frontend:

```sh
npm ci
npm run build
npm run start
```

Use the platform's process management, HTTPS, secret configuration, and request limits. Set the actual API origin before building and configure MongoDB access. Verify hosting terms rather than assuming free deployment.

GET /health checks API liveness. GET /ready also checks student storage and returns 503 when unavailable. A successful health check alone does not prove MongoDB is ready.

## Migration notes

Flask, Jinja templates, handwritten legacy CSS, and the old debug-server entry point have been removed. Home/about and form screens now live in Next.js. /post and /result are replaced by /analyzer; /api/v1.0 teaching URLs are replaced by /api/v1. Update any external clients manually.

The root requirements.txt and Procfile are compatibility entry points for a deployment rooted in python_for_web. Local development instructions above are preferred.

Original learning material: Asabeneh Yetayeh, 30 Days of Python.
