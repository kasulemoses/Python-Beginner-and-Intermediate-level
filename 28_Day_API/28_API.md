# Day 28 — APIs and HTTP

Based on the original 30 Days of Python material by Asabeneh Yetayeh. This lesson uses a local API so exercises do not depend on old hosted demos.

[← Day 27](../27_Day_Python_with_mongodb/27_python_with_mongodb.md) | [Day 29 →](../29_Day_Building_API/29_building_API.md)

## Learning goals

Describe a request/response contract, choose HTTP methods and status codes, inspect JSON, and distinguish CORS from authentication.

An API is an interface between programs. A web API uses HTTP. REST is an architectural style, not a synonym for every API or every CRUD application.

## Request and response

A request has a method, resource URL, headers, and sometimes a body. A response has a status, headers, and sometimes a body. In HTTP/1.1 text notation a request line differs from a response status line. Connections may be reused; they do not have to close after each response. HTTP/2 and HTTP/3 use different wire framing.

```http
POST /api/v1/analysis HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Accept: application/json

{"text":"Python python learning"}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"character_count":22,"word_count":3,"unique_word_count":2,"frequent_words":[{"word":"python","count":2},{"word":"learning","count":1}]}
```

Content-Type describes the representation sent. Accept describes what the client can receive. Path parameters identify a resource; query parameters filter or paginate collections; the JSON body carries structured input.

## Methods and status codes

| Method | Meaning in this project | Typical success |
| --- | --- | --- |
| GET | Read a list or one record; no intended write | 200 |
| POST | Analyze text or create a student | 200 analysis / 201 creation |
| PATCH | Change supplied student fields only | 200 |
| DELETE | Remove an existing student | 204, empty body |
| OPTIONS | Browser cross-origin preflight where applicable | Middleware response |

PUT normally expresses full replacement. We implement PATCH for edits and deliberately omit PUT until full-replacement semantics are taught and tested.

Important errors:
- 404: a valid resource identifier does not exist.
- 422: this FastAPI application's request validation failed.
- 503: required storage is unavailable.
- 401: authentication is missing/invalid, when authentication is added.
- 403: an authenticated caller lacks permission.
- 409: a conflict, when a real application rule creates one. Names are not unique here, so duplicate names do not cause 409.

The implementation returns errors under a detail key; validation errors contain an array of field errors.

## Run local experiments

Start the [application](../python_for_web/README.md), then open http://127.0.0.1:8000/docs. Its OpenAPI definition describes request and response schemas.

```sh
curl -i http://127.0.0.1:8000/health
curl -i -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H 'Content-Type: application/json' -d '{"text":"Python python learning"}'
curl -i -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H 'Content-Type: application/json' -d '{"text":"   "}'
curl -i 'http://127.0.0.1:8000/api/v1/students?limit=0'
```

Expect 200, 200, 422, and 422 respectively with configured student storage. Without storage, student routes can return 503 during dependency resolution. Analysis and health do not require MongoDB.

Browsers can send methods beyond GET: HTML forms support GET/POST, and browser JavaScript fetch can use POST/PATCH/DELETE and others. Postman is optional; use Swagger UI, curl, or the frontend.

## Origins, CORS, and security

An origin consists of scheme, hostname, and port. localhost:3000 and localhost:8000 are different origins.

Our frontend sends same-origin /api/v1 requests through a Next.js rewrite to FastAPI. API_ORIGIN is a server-only frontend setting. Direct browser calls to a different API origin need an explicit CORS allowlist; the backend supports configured CORS_ORIGINS.

CORS is a browser access policy. It does not authenticate users, authorize edits, or protect a public endpoint from non-browser clients. This learning app has no accounts; keep it local and use fictional records. Before public write access, add authentication, authorization, suitable request limits, and transport security.

## Exercises

1. Fill an API contract table: method, URL, request, response, and errors for each student endpoint.
2. Inspect an analyzer submission in browser Developer Tools → Network.
3. Submit missing text, empty text, and a valid paragraph. Compare response bodies and status codes.
4. With MongoDB configured, compare a malformed student ID (422) with an absent valid ID (404).
5. Explain why a successful deletion has no JSON body.
6. Explain when CORS is needed and why it does not secure student writes.
7. Read /openapi.json and find the student request schema.

**You are finished when:** you can explain a real request and response, reproduce validation failures, and distinguish a backend failure from a browser-origin issue.

References: [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html), [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/), [CORS](https://fastapi.tiangolo.com/tutorial/cors/).

[← Day 27](../27_Day_Python_with_mongodb/27_python_with_mongodb.md) | [Day 29 →](../29_Day_Building_API/29_building_API.md)
