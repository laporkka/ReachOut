from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from reachout.src.core.config import settings
from reachout.src.api.v1.auth import router as auth_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"], 
)


app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }