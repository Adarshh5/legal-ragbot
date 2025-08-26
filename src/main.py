from src import app


@app.get("/")
async def root():
    return {"message": "Service is running 🚀"}