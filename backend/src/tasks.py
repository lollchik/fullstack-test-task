import asyncio
import os
from pathlib import Path
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Alert, StoredFile
from src.settings import settings
from src.db_manager import db_manager, get_manager_db_session

REDIS_URL = os.environ.get("REDIS_URL", "redis://backend-redis:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("file_tasks", connection=redis_conn)

engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionMaker = sessionmaker(bind=engine, expire_on_commit=False)


def scan_file_for_threats(file_id: str) -> None:
    asyncio.new_event_loop().run_until_complete(_scan_file_for_threats(file_id))


async def _scan_file_for_threats(file_id: str) -> None:
    db_manager.init(settings.DB_URL)
    async with get_manager_db_session() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        file_item.processing_status = "processing"
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
            reasons.append(f"suspicious extension {extension}")

        if file_item.size > 10 * 1024 * 1024:
            reasons.append("file is larger than 10 MB")

        if extension == ".pdf" and file_item.mime_type not in {
            "application/pdf",
            "application/octet-stream",
        }:
            reasons.append("pdf extension does not match mime type")

        file_item.scan_status = "suspicious" if reasons else "clean"
        file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
        file_item.requires_attention = bool(reasons)
        await session.commit()

    await db_manager.close()
    queue.enqueue(extract_file_metadata, file_id)


def extract_file_metadata(file_id: str) -> None:
    asyncio.new_event_loop().run_until_complete(_send_file_alert(file_id))


async def _extract_file_metadata(file_id: str) -> None:
    db_manager.init(settings.DB_URL)
    async with get_manager_db_session() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        stored_path = settings.STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await session.commit()
            queue.enqueue(send_file_alert, file_id)
            return

        metadata = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if file_item.mime_type.startswith("text/"):
            try:
                with open(stored_path, "r", encoding="utf-8", errors="ignore") as f:
                    char_count = 0
                    line_count = 0
                    for line in f:
                        line_count += 1
                        char_count += len(line)
                metadata["line_count"] = line_count
                metadata["char_count"] = char_count
            except Exception:
                metadata["error"] = "failed to read text data safely"

        elif file_item.mime_type == "application/pdf":
            try:
                pages = 0
                with open(stored_path, "rb") as f:
                    while chunk := f.read(64 * 1024):
                        pages += chunk.count(b"/Type /Page")
                metadata["approx_page_count"] = max(pages, 1)
            except Exception:
                metadata["error"] = "failed to parse pdf data safely"

        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        await session.commit()
        await db_manager.close()
    queue.enqueue(send_file_alert, file_id)


def send_file_alert(file_id: str) -> None:
    asyncio.new_event_loop().run_until_complete(_send_file_alert(file_id))


async def _send_file_alert(file_id: str) -> None:
    db_manager.init(settings.DB_URL)
    async with get_manager_db_session() as session:
        file_item = await session.get(StoredFile, file_id)
        if not file_item:
            return

        if file_item.processing_status == "failed":
            alert = Alert(file_id=file_id, level="critical", message="File processing failed")
        elif file_item.requires_attention:
            alert = Alert(
                file_id=file_id,
                level="warning",
                message=f"File requires attention: {file_item.scan_details}",
            )
        else:
            alert = Alert(file_id=file_id, level="info", message="File processed successfully")

        session.add(alert)
        await session.commit()
        await db_manager.close()
