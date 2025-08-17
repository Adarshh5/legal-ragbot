from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ml-test.shop", "http://127.0.0.1:8000"],  # only your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
