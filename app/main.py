"""FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import config
from app.routes import api, pages

# Create FastAPI app
app = FastAPI(
    title="Omni Embed Demo App",
    description="会員向け購買分析レポート閲覧アプリ",
    version="0.1.0",
    debug=config.DEBUG
)

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(api.router)
app.include_router(pages.router)


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    # In production, use proper logging
    if config.DEBUG:
        print(f"Error: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.on_event("startup")
async def startup_event():
    """Startup event."""
    # Validate configuration (but allow startup even if Omni is not configured)
    try:
        config.validate()
    except ValueError as e:
        print(f"Warning: Configuration incomplete - {e}")
        print("Application will start but Omni features may not work")
