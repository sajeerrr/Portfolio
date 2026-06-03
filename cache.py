"""
cache.py — Simple in-memory cache layer with TTL support.
Stores PortfolioData to avoid hitting GitHub API rate limits on every request.
"""

import time
from typing import Any, Optional
from rich.console import Console

console = Console()


class DataCache:
    """
    In-memory key-value cache with per-entry TTL (time-to-live).
    Each entry stores the value along with its expiration timestamp.
    """

    def __init__(self):
        # Internal store: {key: {"value": Any, "expires_at": float}}
        self._store: dict[str, dict[str, Any]] = {}

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Store a value with a TTL (in seconds).
        After TTL expires, get() will return None for this key.
        """
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        console.log(f"[green]Cache SET[/green]: key='{key}', TTL={ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value. Returns None if the key doesn't exist
        or if the entry has expired.
        """
        entry = self._store.get(key)
        if entry is None:
            return None

        # Check if entry has expired
        if time.time() > entry["expires_at"]:
            console.log(f"[yellow]Cache EXPIRED[/yellow]: key='{key}'")
            del self._store[key]
            return None

        return entry["value"]

    def get_even_if_expired(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value regardless of expiration.
        Used as a fallback when GitHub API is down — serve stale data
        rather than showing nothing.
        """
        entry = self._store.get(key)
        if entry is None:
            return None
        return entry["value"]

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()
        console.log("[red]Cache CLEARED[/red]")


# Singleton cache instance
cache = DataCache()
