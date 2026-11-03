from datetime import datetime, timezone
from typing import Protocol

from bson import ObjectId
from pymongo import ReturnDocument


class StudentRepository(Protocol):
    async def list(self, country: str | None, offset: int, limit: int) -> dict: ...
    async def get(self, student_id: str) -> dict | None: ...
    async def create(self, data: dict) -> dict: ...
    async def update(self, student_id: str, data: dict) -> dict | None: ...
    async def delete(self, student_id: str) -> bool: ...


def serialize(document: dict) -> dict:
    return {**{k: v for k, v in document.items() if k != "_id"}, "id": str(document["_id"])}


class MongoStudentRepository:
    def __init__(self, collection):
        self.collection = collection

    async def list(self, country, offset, limit):
        query = {"country": country} if country else {}
        # _id breaks name ties and makes pagination deterministic.
        cursor = self.collection.find(query).sort([("name", 1), ("_id", 1)]).skip(offset).limit(limit)
        return {
            "items": [serialize(doc) async for doc in cursor],
            "total": await self.collection.count_documents(query),
            "offset": offset, "limit": limit,
        }

    async def get(self, student_id):
        doc = await self.collection.find_one({"_id": ObjectId(student_id)})
        return serialize(doc) if doc else None

    async def create(self, data):
        now = datetime.now(timezone.utc)
        # BSON stores datetimes at millisecond precision. Return the persisted precision.
        now = now.replace(microsecond=(now.microsecond // 1000) * 1000)
        doc = {**data, "created_at": now, "updated_at": now}
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return serialize(doc)

    async def update(self, student_id, data):
        doc = await self.collection.find_one_and_update(
            {"_id": ObjectId(student_id)},
            {"$set": {**data, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return serialize(doc) if doc else None

    async def delete(self, student_id):
        result = await self.collection.delete_one({"_id": ObjectId(student_id)})
        return result.deleted_count == 1
