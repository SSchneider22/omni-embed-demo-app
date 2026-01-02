"""Page routes (HTML)."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth.deps import get_current_user, require_auth
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(get_current_user)):
    """Home page."""
    if user:
        return templates.TemplateResponse(
            "me.html",
            {"request": request, "user": user}
        )
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.get("/me", response_class=HTMLResponse)
async def me_page(request: Request, user: User = Depends(require_auth)):
    """User profile page."""
    return templates.TemplateResponse(
        "me.html",
        {"request": request, "user": user}
    )


@router.get("/embed", response_class=HTMLResponse)
async def embed_page(request: Request, user: User = Depends(require_auth)):
    """Omni embed page."""
    content_path = request.query_params.get("contentPath", "")
    return templates.TemplateResponse(
        "embed.html",
        {"request": request, "user": user, "content_path": content_path}
    )
