"""Explicit, repeatable seed command. Never runs during API startup."""
import asyncio
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import AsyncMongoClient

from .settings import Settings


async def main():
    settings = Settings()
    if not settings.mongodb_uri:
        raise SystemExit("Set MONGODB_URI before seeding")
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
    try:
        collection = client[settings.mongodb_database].students
        # Reserved, fictional tutorial records. $setOnInsert preserves edits on later runs.
        for number, name, country, city in [
            (1, "Alex Learner", "Uganda", "Kampala"),
            (2, "Sam Student", "Kenya", "Nairobi"),
        ]:
            now = datetime.now(timezone.utc)
            await collection.update_one(
                {"_id": ObjectId(f"{number:024x}")},
                {"$setOnInsert": {
                    "name": name, "country": country, "city": city,
                    "date_of_birth": "2000-01-01", "skills": ["Python"],
                    "bio": "Fictional learning record", "created_at": now, "updated_at": now,
                }}, upsert=True,
            )
        print("Seed complete: two fictional records ensured; existing data preserved.")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
