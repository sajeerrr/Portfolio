"""
scheduler.py — APScheduler setup for automatic GitHub data refresh.
Runs a background job every 6 hours to re-fetch portfolio data from GitHub,
keeping the cache fresh without manual intervention.
"""

from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console

from config import settings
from github_service import GitHubService

console = Console()

# Create the async scheduler instance
scheduler = AsyncIOScheduler()


async def refresh_github_data() -> None:
    """
    Scheduled job: re-fetches portfolio data from GitHub and updates the cache.
    This function is called automatically every CACHE_TTL_SECONDS (default: 6 hours).
    The fetch_portfolio_data method handles caching internally.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    console.log(f"[cyan]⏰ Scheduled refresh triggered at {timestamp}[/cyan]")

    try:
        await GitHubService.fetch_portfolio_data(settings.GITHUB_USERNAME)
        console.log("[green]✓ Scheduled refresh completed successfully[/green]")
    except Exception as e:
        console.log(f"[red]✗ Scheduled refresh failed[/red]: {e}")


def start_scheduler() -> None:
    """
    Start the APScheduler with the GitHub data refresh job.
    Runs every CACHE_TTL_SECONDS (default: 21600s = 6 hours).
    """
    scheduler.add_job(
        refresh_github_data,
        trigger=IntervalTrigger(seconds=settings.CACHE_TTL_SECONDS),
        id="github_refresh",
        name="Refresh GitHub Portfolio Data",
        replace_existing=True,
    )
    scheduler.start()
    console.log(
        f"[green]✓ Scheduler started[/green] — "
        f"refreshing every {settings.CACHE_TTL_SECONDS // 3600}h "
        f"({settings.CACHE_TTL_SECONDS}s)"
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        console.log("[yellow]⏹ Scheduler stopped[/yellow]")
