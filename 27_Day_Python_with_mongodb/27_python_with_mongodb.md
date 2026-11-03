# Day 27 — Python with MongoDB

Based on the original 30 Days of Python material by Asabeneh Yetayeh. Examples now use explicit configuration and repeatable data setup.

[← Day 26](../26_Day_Python_web/26_python_web.md) | [Day 28 →](../28_Day_API/28_API.md)

## Learning goals

Model documents, connect Python to MongoDB, query and update records, and understand how database values become API responses.

Prerequisites: dictionaries, lists, exceptions, basic type hints, and Day 26. Use fictional student records.

## Documents and collections

MongoDB stores BSON documents in collections. BSON supports types such as ObjectId and datetime that need conversion for ordinary JSON. Flexible storage does not remove the need for application validation.

Our student schema has name, country, city, date_of_birth, skills, bio, created_at, and updated_at. MongoDB keeps `_id`; API responses expose it as a string `id`. Dates of birth are ISO date strings; timestamps are UTC datetimes in storage and ISO strings in JSON. Use date_of_birth consistently rather than mixing age and birthyear.

## Configure a database

Follow the [setup guide](../python_for_web/README.md). Choose a local MongoDB instance or an Atlas connection that you control. Restrict network access, use a database user with only necessary permissions, and put its URI in the ignored backend `.env`.

Never paste real credentials into lessons or commit them. `.env.example` contains placeholders only.

From `python_for_web/backend`:

```sh
.venv/bin/python -m app.seed
.venv/bin/python -m app.seed
```

Both runs ensure the same two fictional records. The seed command uses stable reserved IDs and `$setOnInsert`: existing edits are preserved. Database writes do not run at module import or during server reload.

## A complete standalone query

This example does not need a running web server. Run it from `python_for_web/backend` after configuration and seeding:

```py
from pymongo import MongoClient
from app.settings import Settings

settings = Settings()
if not settings.mongodb_uri:
    raise RuntimeError("Configure MONGODB_URI first")

with MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000, tz_aware=True) as client:
    db = client[settings.mongodb_database]
    client.admin.command("ping")
    for student in db.students.find({"country": "Uganda"}, {"name": 1, "city": 1}).sort("name", 1).limit(10):
        print(student["name"], student["city"])
```

Selecting `client[database]` does not itself persist a database. A write creates the collection/database as needed.

## Read, update, and delete

- `find_one({"_id": ObjectId(id)})`: one matching document or None.
- `find(query)`: a cursor over matching documents.
- `find(query, projection)`: select returned fields.
- `sort`, `skip`, and `limit`: controlled ordering and pagination.
- `update_one(query, {"$set": changes})`: modify named fields.
- `replace_one(query, full_document)`: replace a document deliberately.
- `delete_one(query)`: delete one matched record; check deleted_count.

Validate an ID before constructing ObjectId. Check matched_count for updates: modified_count can be zero when the record exists but the value is unchanged.

Keep created_at unchanged on edits; set updated_at instead. Use exact IDs for changes rather than names, which need not be unique.

Practice deletion only in a disposable exercise database. An empty delete_many filter removes all documents; dropping a collection removes its data and indexes. Neither operation is part of the normal application or seed command.

## Async FastAPI integration

Read [students.py](../python_for_web/backend/app/students.py) and [main.py](../python_for_web/backend/app/main.py).

The application:
1. Creates one AsyncMongoClient per process during lifespan startup.
2. Pings storage and prepares indexes.
3. Reuses a student repository through dependency injection.
4. Closes the client at shutdown.
5. Reports unavailable storage with 503, without exposing connection details.

Synchronous PyMongo is fine for the standalone exercise above. In async handlers use the async client and await I/O. Do not simply place blocking database calls inside async def.

Indexes cover name/id ordering and country/name/id filtering. A name is not unique. Lists are bounded to at most 100 entries per request. Offset pagination is suitable for this small exercise; large datasets need further pagination design.

## Exercises

1. Seed twice and confirm only two seed records exist.
2. List students in Uganda and verify the returned country.
3. Update the seed learner's city through the API; seed again and verify the edit remains.
4. Add two learners with the same name and explain why IDs differ.
5. Compare full-document replacement with a $set update.
6. Stop MongoDB after API startup and check /ready and student endpoints.
7. Run real database integration tests as described in the setup guide; they use temporary databases with random names.

**You are finished when:** records persist across API restarts, seeding is repeatable, IDs serialize correctly, and errors do not leak credentials.

References: [MongoDB CRUD](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/), [PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/), [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/).

[← Day 26](../26_Day_Python_web/26_python_web.md) | [Day 28 →](../28_Day_API/28_API.md)
