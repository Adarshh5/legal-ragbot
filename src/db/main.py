from sqlmodel import  SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config
import ssl
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

ssl_context = ssl.create_default_context()

asnyc_engine = create_async_engine(
    Config.DATABASE_URL.replace("?sslmode=require", ""),
    connect_args={"ssl": ssl_context}
)

async def initdb() -> None:

    async with asnyc_engine.begin() as conn:

        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session()-> AsyncSession:

    Session = sessionmaker(
        bind=asnyc_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with Session() as session:
        yield session