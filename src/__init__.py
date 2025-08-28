from fastapi import FastAPI, status
from src.auth.routers import auth_router
from src.ragbot.routers import chat_router
from src.ml_model.routers import ml_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ml-test.shop", "http://127.0.0.1:5500"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])

app.include_router(chat_router, prefix=f"/api/{version}/chatbot", tags=["chatbot"])
app.include_router(ml_router, prefix=f"/api/{version}/ml", tags=["predict"])