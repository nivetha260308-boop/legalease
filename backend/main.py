from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from backend.api.routes import router

from backend.utils.config import (
    get_settings,
)


settings = get_settings()


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description=(
        "AI-powered legal document "
        "drafting backend."
    ),
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=(
        settings.cors_origins
    ),

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST",
    ],

    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "service": "LegalEase API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():

    demo_mode = (
        settings.demo_mode
        or not bool(settings.gemini_api_key)
    )

    return {
        "status": "ok",
        "demo_mode": demo_mode,
        "model": settings.gemini_model,
    }