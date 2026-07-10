from fastapi import APIRouter
from fastapi import Depends
from fastapi import File, Form, UploadFile
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db_manager import get_db_session
from src.schemas import FileItem, FileUpdate
from src.services.file import create_file, delete_file, get_file, list_files, update_file
from src.settings import settings
from src.tasks import queue, scan_file_for_threats

router = APIRouter(tags=["files"])


@router.get("/files", response_model=list[FileItem])
async def list_files_view(session: AsyncSession = Depends(get_db_session)):
    return await list_files(session)


@router.post("/files", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
):
    file_item = await create_file(title=title, upload_file=file, session=session)
    queue.enqueue(scan_file_for_threats, file_item.id)
    return file_item


@router.get("/files/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, session: AsyncSession = Depends(get_db_session)):
    return await get_file(file_id, session=session)


@router.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str, payload: FileUpdate, session: AsyncSession = Depends(get_db_session)
):
    return await update_file(file_id=file_id, title=payload.title, session=session)


@router.get("/files/{file_id}/download")
async def download_file(file_id: str, session: AsyncSession = Depends(get_db_session)):
    file_item = await get_file(file_id, session=session)
    stored_path = settings.STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str, session: AsyncSession = Depends(get_db_session)):
    await delete_file(file_id, session=session)


# @router.post("/work-contexts", status_code=201)
# # @require_permissions("user.edit")
# async def add_work_context(
#     request: WorkContextSchema,
#     user: Annotated[AuthorizedUserSchema, Depends(get_authorized_user)],
#     use_case: Annotated[CreateWorkContextUseCase, Depends(get_create_work_context_use_case)],
# ) -> OkResponseSchema:
#     return await use_case.execute(request, user.id)
