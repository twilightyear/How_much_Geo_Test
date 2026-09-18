import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.model import router as model_router

app = FastAPI()



# .env에서 허용 주소 읽기
raw_origins = os.getenv("ALLOW_ORIGINS", "*")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.include_router(model_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)