# main.py
from fastapi import FastAPI
from api.routes import router as generation_router

app = FastAPI(title="LLM Generation API")

app.include_router(generation_router)
