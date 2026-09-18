from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from reachout.src.api.v1.auth import router as auth_router
from reachout.src.api.v1.contacts import router as contact_router
from reachout.src.api.v1.campaigns import router as campaign_router
from reachout.src.api.v1.template import router as template_router
from reachout.src.api.v1.analytics import router as analytic_router

from reachout.src.core.config import settings
from reachout.src.core.logging import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация компонентов системы...")
    
    start_banner = """
    ========================================================
    🚀 REACHOUT CRM API УСПЕШНО ЗАПУЩЕН И ГОТОВ К РАБОТЕ!
    ========================================================
    🔹 Окружение: Production (Docker)
    🔹 База данных: PostgreSQL (reachout)
    🔹 Кэш/Блэклист: Redis DB 0
    🔹 Документация: http://127.0.0
    ========================================================
    """
    logger.success(start_banner)
    
    yield 
    
    logger.warning("FastAPI Server останавливается. Завершение активных сессий...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"], 
)


app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(campaign_router)
app.include_router(template_router)
app.include_router(analytic_router)


@app.get("/")
async def root():
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }