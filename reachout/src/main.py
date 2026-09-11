from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from reachout.src.api.v1.auth import router as auth_router
from reachout.src.api.v1.contacts import router as contact_router
from reachout.src.api.v1.campaigns import router as campaign_router
from reachout.src.api.v1.template import router as template_router

from reachout.src.core.config import settings


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
app.include_router(contact_router)
app.include_router(campaign_router)
app.include_router(template_router)


@app.get("/")
async def root():
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }