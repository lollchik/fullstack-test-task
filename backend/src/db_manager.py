from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from contextlib import asynccontextmanager


class DatabaseManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def init(self, db_url: str) -> None:
        if self._engine is not None:
            return

        self._engine = create_async_engine(db_url)
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("DatabaseManager не инициализирован")
        return self._session_maker

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None


db_manager = DatabaseManager()


@asynccontextmanager
async def get_manager_db_session():
    async with db_manager.session_maker() as session:
        yield session


async def get_db_session():
    async with db_manager.session_maker() as session:
        yield session
