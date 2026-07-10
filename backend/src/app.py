from contextlib import asynccontextmanager
from src.api import v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.settings import settings
from src.db_manager import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.init(settings.DB_URL)
    yield
    await db_manager.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router)
