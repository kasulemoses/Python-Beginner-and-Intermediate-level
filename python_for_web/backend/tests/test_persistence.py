import os
import subprocess
import sys
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from pymongo import MongoClient

from app.main import create_app
from app.settings import Settings


def test_seed_is_repeatable_and_records_survive_api_restart():
    uri = os.environ.get("MONGODB_TEST_URI")
    if not uri:
        pytest.skip("Set MONGODB_TEST_URI for real persistence and seed checks")
    database = "python_learning_test_" + uuid4().hex
    environment = {**os.environ, "MONGODB_URI": uri, "MONGODB_DATABASE": database}
    settings = Settings(mongodb_uri=uri, mongodb_database=database)
    try:
        for _ in range(2):
            subprocess.run([sys.executable, "-m", "app.seed"], env=environment, check=True, capture_output=True)
        with TestClient(create_app(settings)) as client:
            records = client.get("/api/v1/students").json()
            assert records["total"] == 2
            student = records["items"][0]
            url = "/api/v1/students/" + student["id"]
            assert client.patch(url, json={"city": "Seed-preserved city"}).status_code == 200
        # A fresh application lifespan and database client must read the persisted change.
        subprocess.run([sys.executable, "-m", "app.seed"], env=environment, check=True, capture_output=True)
        with TestClient(create_app(settings)) as restarted:
            assert restarted.get(url).json()["city"] == "Seed-preserved city"
            assert restarted.get("/api/v1/students").json()["total"] == 2
    finally:
        with MongoClient(uri, serverSelectionTimeoutMS=3000) as client:
            client.drop_database(database)
