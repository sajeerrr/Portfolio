"""
models.py — Pydantic data models for GitHub API response parsing.
These models define the shape of data flowing through the application,
from GitHub API responses to the template context.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GitHubRepo(BaseModel):
    """
    Represents a single GitHub repository.
    Fields map directly to the GitHub REST API /repos response.
    """
    name: str = ""
    description: Optional[str] = None
    html_url: str = ""
    homepage: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    topics: list[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    fork: bool = False  # Used to filter out forked repos


class GitHubProfile(BaseModel):
    """
    Represents a GitHub user profile.
    Fields map to the GitHub REST API /users/{username} response.
    """
    login: str = ""
    name: Optional[str] = None
    avatar_url: str = ""
    bio: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    html_url: str = ""


class PortfolioData(BaseModel):
    """
    Combined portfolio data served to the frontend.
    Contains the user profile, their repos, and a timestamp of the last update.
    """
    profile: GitHubProfile = Field(default_factory=GitHubProfile)
    repos: list[GitHubRepo] = Field(default_factory=list)
    last_updated: Optional[datetime] = None
