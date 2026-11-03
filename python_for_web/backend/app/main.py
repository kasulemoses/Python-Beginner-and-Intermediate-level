from contextlib import asynccontextmanager
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from .analysis import analyze
from .schemas import AnalysisRequest, AnalysisResult, StudentCreate, StudentPage, StudentRead, StudentUpdate
from .settings import Settings
from .students import MongoStudentRepository, StudentRepository


def get_repository(request: Request) -> StudentRepository:
    repo = request.app.state.student_repository
    if repo is None:
        raise HTTPException(503, "Student storage is unavailable. Configure MongoDB and restart the API.")
    return repo


Repository = Annotated[StudentRepository, Depends(get_repository)]


def checked_id(student_id: str) -> str:
    if not ObjectId.is_valid(student_id):
        raise HTTPException(422, "Student id must be a 24-character hexadecimal ObjectId")
    return student_id


StudentId = Annotated[str, Depends(checked_id)]


def create_app(settings: Settings | None = None, repository: StudentRepository | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.student_repository = repository
        client = None
        if repository is None and settings.mongodb_uri:
            client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000, tz_aware=True)
            try:
                await client.admin.command("ping")
                collection = client[settings.mongodb_database].students
                await collection.create_index([("name", 1), ("_id", 1)])
                await collection.create_index([("country", 1), ("name", 1), ("_id", 1)])
                app.state.student_repository = MongoStudentRepository(collection)
            except PyMongoError:
                # Analysis still works; readiness reports storage failure without leaking the URI.
                app.state.student_repository = None
        try:
            yield
        finally:
            if client is not None:
                await client.close()

    app = FastAPI(title="Python Learning API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                       allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type"])

    @app.exception_handler(PyMongoError)
    async def database_failure(request: Request, exc: PyMongoError):
        return JSONResponse(status_code=503, content={"detail": "Student storage is temporarily unavailable"})

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(request: Request):
        repo = get_repository(request)
        # Probe a bounded query so readiness also notices a database that failed after startup.
        await repo.list(None, 0, 1)
        return {"status": "ready"}

    router = APIRouter(prefix="/api/v1")

    @router.post("/analysis", response_model=AnalysisResult)
    def analysis(payload: AnalysisRequest):
        return analyze(payload.text)

    @router.get("/students", response_model=StudentPage)
    async def students(repo: Repository, country: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
                       offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
                       limit: Annotated[int, Query(ge=1, le=100)] = 10):
        return await repo.list(country, offset, limit)

    @router.post("/students", response_model=StudentRead, status_code=201)
    async def create_student(payload: StudentCreate, repo: Repository, response: Response):
        doc = await repo.create(payload.model_dump(mode="json"))
        response.headers["Location"] = "/api/v1/students/" + doc["id"]
        return doc

    @router.get("/students/{student_id}", response_model=StudentRead)
    async def student(student_id: StudentId, repo: Repository):
        doc = await repo.get(student_id)
        if doc is None:
            raise HTTPException(404, "Student not found")
        return doc

    @router.patch("/students/{student_id}", response_model=StudentRead)
    async def update_student(student_id: StudentId, payload: StudentUpdate, repo: Repository):
        doc = await repo.update(student_id, payload.model_dump(mode="json", exclude_unset=True))
        if doc is None:
            raise HTTPException(404, "Student not found")
        return doc

    @router.delete("/students/{student_id}", status_code=204)
    async def delete_student(student_id: StudentId, repo: Repository):
        if not await repo.delete(student_id):
            raise HTTPException(404, "Student not found")
        return Response(status_code=204)

    app.include_router(router)
    return app


app = create_app()
