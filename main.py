"""
main.py — FastAPI application entry point.
Serves the portfolio website, handles API routes, and manages the app lifecycle.
All routes, middleware, and startup/shutdown logic live here.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import secrets

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

from config import settings
from cache import cache
from models import PortfolioData
from github_service import GitHubService
from scheduler import start_scheduler, stop_scheduler
from admin_storage import (
    verify_admin_password, load_settings, save_settings,
    get_display_stats, should_show_events, get_excluded_repos,
    add_excluded_repo, remove_excluded_repo, filter_repos_by_admin,
    load_selected_projects, save_selected_projects,
    get_content, update_about, update_skills, update_certificates,
    update_settings
)

console = Console()
ADMIN_SESSION_COOKIE = "portfolio_admin_session"
ADMIN_SESSION_TOKEN = secrets.token_urlsafe(32)

# Get the absolute path to the project directory
BASE_DIR = Path(__file__).parent

# Initialize Jinja2 environment for template rendering
jinja_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — runs on app startup and shutdown.
    Startup: Fetch initial GitHub data, populate cache, start scheduler.
    Shutdown: Stop the scheduler gracefully.
    """
    # === STARTUP ===
    console.rule("[bold green]Portfolio App Starting[/bold green]")
    console.log(f"GitHub User: [bold]{settings.GITHUB_USERNAME}[/bold]")

    # Fetch GitHub data on first launch to populate cache
    try:
        await GitHubService.fetch_portfolio_data(settings.GITHUB_USERNAME)
    except Exception as e:
        console.log(f"[red]⚠ Initial data fetch failed: {e}[/red]")
        console.log("[yellow]App will serve with empty data until next refresh[/yellow]")

    # Start the background scheduler for periodic refreshes
    start_scheduler()
    console.rule("[bold green]App Ready — Serving on port {0}[/bold green]".format(settings.PORT))

    yield  # App is running

    # === SHUTDOWN ===
    console.rule("[bold yellow]Shutting Down[/bold yellow]")
    stop_scheduler()
    console.log("[green]Goodbye! 👋[/green]")


# Create the FastAPI application
app = FastAPI(
    title="Sajeer F M — Portfolio",
    description="Personal portfolio website powered by FastAPI + GitHub API",
    version="2.0.0",
    lifespan=lifespan,
)

# --- Middleware ---
# CORS: Allow all origins for API access (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files & Templates ---
# Mount static directory for CSS, JS, and other assets
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def get_portfolio_data() -> PortfolioData:
    """
    Helper: Retrieve portfolio data from cache.
    Falls back to stale cache data, then to an empty PortfolioData if nothing is available.
    """
    # Try fresh cache first
    data = cache.get("portfolio")
    if data:
        return data

    # Try stale cache as fallback
    data = cache.get_even_if_expired("portfolio")
    if data:
        console.log("[yellow]Serving stale cached data[/yellow]")
        return data

    # No data available at all
    return PortfolioData(last_updated=datetime.now(timezone.utc))


def get_admin_filtered_portfolio_data() -> PortfolioData:
    """
    Helper: Return portfolio data after applying admin project visibility settings.
    Keeps the HTML route and JSON API in sync.
    """
    portfolio = get_portfolio_data()
    return portfolio.model_copy(update={"repos": filter_repos_by_admin(portfolio.repos)})


def is_admin_authenticated(request: Request) -> bool:
    """Check the signed-in admin session cookie for protected admin APIs."""
    return request.cookies.get(ADMIN_SESSION_COOKIE) == ADMIN_SESSION_TOKEN


def admin_unauthorized_response() -> JSONResponse:
    """Consistent unauthorized response for admin API calls."""
    return JSONResponse(
        status_code=401,
        content={"status": "unauthorized", "message": "Admin login required"},
    )


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Main page route — renders the single-page portfolio HTML.
    Injects portfolio data into the Jinja2 template context so the
    initial page load has data without needing a JS fetch.
    """
    portfolio = get_admin_filtered_portfolio_data()
    display_stats = get_display_stats()
    show_events = should_show_events()
    
    # Render template using Jinja2
    template = jinja_env.get_template("index.html")
    html_content = template.render(
        request=request,
        portfolio=portfolio,
        profile=portfolio.profile,
        repos=portfolio.repos,
        last_updated=portfolio.last_updated,
        display_stats=display_stats,
        show_events=show_events,
    )
    
    return HTMLResponse(content=html_content)


@app.get("/api/github")
async def api_github():
    """
    JSON API endpoint — returns raw portfolio data.
    Used by frontend JavaScript to dynamically update project cards
    without a full page reload.
    """
    portfolio = get_admin_filtered_portfolio_data()
    return portfolio.model_dump(mode="json")


@app.post("/api/refresh")
async def api_refresh():
    """
    Manual refresh endpoint — re-fetches GitHub data immediately.
    Called when user clicks the "Refresh Projects" button.
    Returns the updated portfolio data along with a status message.
    """
    console.log("[cyan]🔄 Manual refresh triggered[/cyan]")
    try:
        portfolio = await GitHubService.fetch_portfolio_data(settings.GITHUB_USERNAME)
        filtered_portfolio = portfolio.model_copy(update={"repos": filter_repos_by_admin(portfolio.repos)})
        return {
            "status": "refreshed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": filtered_portfolio.model_dump(mode="json"),
        }
    except Exception as e:
        console.log(f"[red]✗ Manual refresh failed: {e}[/red]")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )


@app.post("/api/contact")
async def api_contact(request: Request):
    """
    Contact form endpoint — receives form data and logs it.
    In production, this could send an email or store in a database.
    """
    form_data = await request.json()
    console.log(f"[bold magenta]📬 New Contact Message[/bold magenta]")
    console.log(f"  Name:    {form_data.get('name', 'N/A')}")
    console.log(f"  Email:   {form_data.get('email', 'N/A')}")
    console.log(f"  Message: {form_data.get('message', 'N/A')[:100]}...")
    return {"status": "sent", "message": "Thank you! Your message has been received."}


# ============ ADMIN ROUTES ============

@app.post("/admin/login")
async def admin_login(request: Request, response: Response):
    """
    Admin authentication endpoint.
    Verify password and return access status.
    """
    data = await request.json()
    password = data.get("password", "")

    if verify_admin_password(password):
        response.set_cookie(
            ADMIN_SESSION_COOKIE,
            ADMIN_SESSION_TOKEN,
            max_age=60 * 60 * 4,
            httponly=True,
            samesite="strict",
        )
        console.log("[green]✓ Admin login successful[/green]")
        return {
            "status": "authenticated",
            "message": "Welcome to admin panel!",
            "access": "granted",
        }
    else:
        console.log("[red]✗ Admin login failed - incorrect password[/red]")
        return JSONResponse(
            status_code=401,
            content={"status": "unauthorized", "message": "Invalid password"},
        )


@app.post("/admin/logout")
async def admin_logout(response: Response):
    """Clear the admin session cookie."""
    response.delete_cookie(ADMIN_SESSION_COOKIE)
    return {"status": "logged_out"}


@app.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    """
    Get admin dashboard data with current settings.
    """
    if not is_admin_authenticated(request):
        return admin_unauthorized_response()

    portfolio = get_portfolio_data()
    excluded_repos = get_excluded_repos()
    display_stats = get_display_stats()
    
    # Filter repos based on admin settings
    filtered_repos = filter_repos_by_admin(portfolio.repos)
    
    return {
        "status": "ok",
        "total_repos": len(portfolio.repos),
        "displayed_repos": len(filtered_repos),
        "excluded_repos": excluded_repos,
        "display_stats": display_stats,
        "show_events": should_show_events(),
        "repos": [
            {
                "name": repo.name,
                "description": repo.description,
                "url": repo.html_url,
                "language": repo.language,
                "excluded": repo.name in excluded_repos,
            }
            for repo in portfolio.repos
        ],
    }


@app.post("/admin/settings/stats")
async def admin_update_stats(request: Request):
    """
    Update display statistics (repos, followers, years exp).
    """
    if not is_admin_authenticated(request):
        return admin_unauthorized_response()

    data = await request.json()
    settings_data = load_settings()
    
    stats = data.get("display_stats", {})
    settings_data["display_stats"] = {
        "repos": stats.get("repos", 0),
        "followers": stats.get("followers", 0),
        "years_exp": stats.get("years_exp", 2),
    }
    
    if save_settings(settings_data):
        console.log("[green]✓ Stats updated[/green]")
        return {"status": "updated", "display_stats": settings_data["display_stats"]}
    
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Failed to save settings"},
    )


@app.post("/admin/settings/events")
async def admin_toggle_events(request: Request):
    """
    Toggle Activities & Events section display.
    """
    if not is_admin_authenticated(request):
        return admin_unauthorized_response()

    data = await request.json()
    show_events = data.get("show_events", False)
    
    if update_settings("show_events", show_events):
        console.log(f"[green]✓ Events display: {show_events}[/green]")
        return {"status": "updated", "show_events": show_events}
    
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Failed to save settings"},
    )


@app.post("/admin/projects/exclude")
async def admin_exclude_project(request: Request):
    """
    Exclude a project from display.
    """
    if not is_admin_authenticated(request):
        return admin_unauthorized_response()

    data = await request.json()
    repo_name = data.get("repo_name")
    
    if not repo_name:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "repo_name required"},
        )
    
    if add_excluded_repo(repo_name):
        console.log(f"[green]✓ Project excluded: {repo_name}[/green]")
        return {"status": "excluded", "repo_name": repo_name}
    
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Failed to exclude project"},
    )


@app.post("/admin/projects/include")
async def admin_include_project(request: Request):
    """
    Include a previously excluded project.
    """
    if not is_admin_authenticated(request):
        return admin_unauthorized_response()

    data = await request.json()
    repo_name = data.get("repo_name")
    
    if not repo_name:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "repo_name required"},
        )
    
    if remove_excluded_repo(repo_name):
        console.log(f"[green]✓ Project included: {repo_name}[/green]")
        return {"status": "included", "repo_name": repo_name}
    
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Failed to include project"},
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """
    Admin dashboard interface at /admin
    """
    template = jinja_env.get_template("admin.html")
    html_content = template.render()
    return HTMLResponse(content=html_content)


# --- Run with uvicorn ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
