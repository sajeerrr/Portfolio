"""
github_service.py — All GitHub API logic.
Handles fetching user profile and repository data from the GitHub REST API
using async HTTP calls via httpx. Includes error handling and fallback to cached data.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

import httpx
from rich.console import Console

from config import settings
from models import GitHubProfile, GitHubRepo, PortfolioData
from cache import cache

console = Console()

# Standard headers for GitHub API v3
GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}

# Only add Authorization header if a token is provided
if settings.GITHUB_TOKEN and settings.GITHUB_TOKEN != "your_personal_access_token_here":
    GITHUB_API_HEADERS["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"


class GitHubService:
    """
    Async service class for interacting with the GitHub REST API.
    All methods use httpx.AsyncClient for non-blocking HTTP requests.
    """

    @staticmethod
    async def fetch_profile(username: str) -> Optional[GitHubProfile]:
        """
        Fetch a GitHub user's profile data.
        Endpoint: GET https://api.github.com/users/{username}
        Returns a GitHubProfile model or None on failure.
        """
        url = f"https://api.github.com/users/{username}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=GITHUB_API_HEADERS)
                response.raise_for_status()
                data = response.json()
                profile = GitHubProfile(**data)
                console.log(f"[green]✓[/green] Fetched profile for [bold]{username}[/bold]")
                return profile
        except httpx.HTTPStatusError as e:
            console.log(f"[red]✗ GitHub API error[/red]: {e.response.status_code} — {e.response.text[:200]}")
            return None
        except Exception as e:
            console.log(f"[red]✗ Failed to fetch profile[/red]: {e}")
            return None

    @staticmethod
    async def fetch_repos(username: str) -> list[GitHubRepo]:
        """
        Fetch a GitHub user's repositories, sorted by most recently updated.
        Filters out forked repos — only shows original work.
        Endpoint: GET https://api.github.com/users/{username}/repos?sort=updated&per_page=30
        """
        url = f"https://api.github.com/users/{username}/repos"
        params = {"sort": "updated", "per_page": 30}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=GITHUB_API_HEADERS, params=params)
                response.raise_for_status()
                data = response.json()

                # Parse all repos and filter out forks
                all_repos = [GitHubRepo(**repo) for repo in data]
                original_repos = [repo for repo in all_repos if not repo.fork]

                console.log(
                    f"[green]✓[/green] Fetched [bold]{len(original_repos)}[/bold] repos "
                    f"(filtered {len(all_repos) - len(original_repos)} forks)"
                )
                return original_repos
        except httpx.HTTPStatusError as e:
            console.log(f"[red]✗ GitHub API error[/red]: {e.response.status_code} — {e.response.text[:200]}")
            return []
        except Exception as e:
            console.log(f"[red]✗ Failed to fetch repos[/red]: {e}")
            return []

    @staticmethod
    async def fetch_portfolio_data(username: str) -> PortfolioData:
        """
        Fetch both profile and repos concurrently using asyncio.gather().
        Combines them into a single PortfolioData model with a timestamp.
        Falls back to cached data if the API call fails.
        """
        console.log(f"[cyan]⟳ Fetching portfolio data for [bold]{username}[/bold]...[/cyan]")

        # Concurrent fetch — profile and repos at the same time
        profile, repos = await asyncio.gather(
            GitHubService.fetch_profile(username),
            GitHubService.fetch_repos(username),
        )

        # If both calls failed, try to return cached data as fallback
        if profile is None and not repos:
            console.log("[yellow]⚠ Both API calls failed — attempting cache fallback[/yellow]")
            cached = cache.get_even_if_expired("portfolio")
            if cached:
                console.log("[yellow]↩ Returning stale cached data[/yellow]")
                return cached
            # No cache available — return empty data
            console.log("[red]✗ No cached data available — returning empty portfolio[/red]")
            return PortfolioData(last_updated=datetime.now(timezone.utc))

        # Build the portfolio data object
        portfolio = PortfolioData(
            profile=profile or GitHubProfile(),
            repos=repos,
            last_updated=datetime.now(timezone.utc),
        )

        # Update the cache with fresh data
        cache.set("portfolio", portfolio, settings.CACHE_TTL_SECONDS)
        console.log(f"[green]✓ Portfolio data cached[/green] (TTL: {settings.CACHE_TTL_SECONDS}s)")

        return portfolio
