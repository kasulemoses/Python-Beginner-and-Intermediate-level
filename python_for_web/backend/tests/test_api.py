from copy import deepcopy
from datetime import datetime, timezone
import os
from uuid import uuid4

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from app.main import create_app
from app.settings import Settings

STUDENT = {"name": "Test Learner", "country": "Uganda", "city": "Kampala",
           "date_of_birth": "2001-02-03", "skills": ["Python"], "bio": "Fictional"}


class MemoryRepository:
    """API boundary test double; real MongoDB is also exercised when configured."""
    def __init__(self):
        self.docs = {}

    async def list(self, country, offset, limit):
        docs = sorted([d for d in self.docs.values() if not country or d["country"] == country],
                      key=lambda d: (d["name"], d["id"]))
        return {"items": deepcopy(docs[offset:offset + limit]), "total": len(docs), "offset": offset, "limit": limit}

    async def get(self, student_id):
        return deepcopy(self.docs.get(student_id))

    async def create(self, data):
        now = datetime.now(timezone.utc)
        doc = {**data, "id": str(ObjectId()), "created_at": now, "updated_at": now}
        self.docs[doc["id"]] = doc
        return deepcopy(doc)

    async def update(self, student_id, data):
        if student_id not in self.docs:
            return None
        self.docs[student_id].update(data, updated_at=datetime.now(timezone.utc))
        return deepcopy(self.docs[student_id])

    async def delete(self, student_id):
        return self.docs.pop(student_id, None) is not None


@pytest.fixture(params=["memory", "mongo"])
def client(request):
    if request.param == "memory":
        with TestClient(create_app(Settings(mongodb_uri=None), MemoryRepository())) as client:
            yield client
        return
    uri = os.environ.get("MONGODB_TEST_URI")
    if not uri:
        pytest.skip("Set MONGODB_TEST_URI to run real MongoDB integration tests")
    database = "python_learning_test_" + uuid4().hex
    try:
        with TestClient(create_app(Settings(mongodb_uri=uri, mongodb_database=database))) as client:
            assert client.get("/ready").status_code == 200
            yield client
    finally:
        with MongoClient(uri, serverSelectionTimeoutMS=3000) as mongo:
            mongo.drop_database(database)


def test_crud_and_pagination(client):
    response = client.post("/api/v1/students", json=STUDENT)
    assert response.status_code == 201
    original = response.json()
    url = "/api/v1/students/" + original["id"]
    assert response.headers["location"] == url
    assert client.get(url).json() == original
    second = client.post("/api/v1/students", json={**STUDENT, "name": "Zed", "country": "Kenya"}).json()
    page = client.get("/api/v1/students?limit=1").json()
    assert page["total"] == 2 and len(page["items"]) == 1
    assert client.get("/api/v1/students?offset=1&limit=1").json()["items"][0]["id"] == second["id"]
    filtered = client.get("/api/v1/students?country=Uganda").json()
    assert filtered["total"] == 1
    assert client.get("/api/v1/students?country=Missing").json()["items"] == []
    update = client.patch(url, json={"city": "Jinja", "skills": []})
    assert update.status_code == 200
    updated = update.json()
    assert updated["city"] == "Jinja" and updated["skills"] == []
    assert updated["name"] == original["name"]
    assert updated["created_at"] == original["created_at"]
    assert updated["updated_at"] >= original["updated_at"]
    assert client.get(url).json() == updated
    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404
    assert client.delete(url).status_code == 404


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_ids_and_missing(client, method):
    kwargs = {"json": {"city": "Jinja"}} if method == "patch" else {}
    assert getattr(client, method)("/api/v1/students/bad", **kwargs).status_code == 422
    assert getattr(client, method)("/api/v1/students/" + str(ObjectId()), **kwargs).status_code == 404


@pytest.mark.parametrize("patch", [{}, {"name": " "}, {"country": None}, {"unexpected": 1},
                                  {"date_of_birth": "2999-01-01"}, {"skills": [" "]}])
def test_invalid_updates(client, patch):
    student = client.post("/api/v1/students", json=STUDENT).json()
    assert client.patch("/api/v1/students/" + student["id"], json=patch).status_code == 422
    assert client.get("/api/v1/students/" + student["id"]).json() == student


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1", "country="])
def test_invalid_pagination(client, query):
    assert client.get("/api/v1/students?" + query).status_code == 422


def test_analysis_and_unconfigured_database():
    with TestClient(create_app(Settings(mongodb_uri=None))) as client:
        response = client.post("/api/v1/analysis", json={"text": " Python, PYTHON! café café. "})
        assert response.status_code == 200
        result = response.json()
        assert result["character_count"] == 28
        assert result["word_count"] == 4 and result["unique_word_count"] == 2
        assert result["frequent_words"] == [{"word": "café", "count": 2}, {"word": "python", "count": 2}]
        for text in ["", "   ", "x" * 50001]:
            assert client.post("/api/v1/analysis", json={"text": text}).status_code == 422
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
        assert client.get("/api/v1/students").status_code == 503


def test_database_failure_is_safe():
    class BrokenRepository(MemoryRepository):
        async def list(self, *args):
            raise AutoReconnect("private connection details")
    with TestClient(create_app(Settings(mongodb_uri=None), BrokenRepository())) as client:
        response = client.get("/api/v1/students")
        assert response.status_code == 503
        assert "private" not in response.text
        assert client.get("/ready").status_code == 503


def test_cors():
    with TestClient(create_app(Settings(mongodb_uri=None))) as client:
        for origin, allowed in [("http://localhost:3000", True), ("https://untrusted.example", False)]:
            response = client.options("/api/v1/students", headers={
                "Origin": origin, "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            })
            assert ("access-control-allow-origin" in response.headers) is allowed
