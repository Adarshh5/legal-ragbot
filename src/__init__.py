from fastapi import FastAPI, status
from src.auth.routers import auth_router
from src.ragbot.routers import chat_router
from contextlib import asynccontextmanager


@asynccontextmanager

async def lifespan(app: FastAPI):
    print("Server is starting...")
    # await initdb()
    yield
    print("server is stopping")



version = "v1"

app = FastAPI(
    title="RAGBOT",
    description="A REST API FOR RAG BASED Q&A",
    version=version,
    lifespan=lifespan,
)


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])

app.include_router(chat_router, prefix=f"/api/{version}/chatbot", tags=["chatbot"])