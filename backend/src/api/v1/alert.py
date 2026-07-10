from fastapi import APIRouter

from src.schemas import AlertItem
from src.services.alert import list_alerts
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db_manager import get_db_session

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view(session: AsyncSession = Depends(get_db_session)):
    return await list_alerts(session)
