"""
admin_storage.py — Admin settings storage and management.
Uses JSON file for persistent storage of admin configurations.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console

console = Console()

# Path to admin data file
ADMIN_DIR = Path(__file__).parent / "admin_data"
ADMIN_DIR.mkdir(exist_ok=True)

ADMIN_FILE = ADMIN_DIR / "admin_settings.json"
PROJECTS_FILE = ADMIN_DIR / "selected_projects.json"
CREDENTIALS_FILE = ADMIN_DIR / ".admin_credentials"


# Default admin settings
DEFAULT_SETTINGS = {
    "show_events": False,  # Toggle Activities & Events section
    "display_stats": {
        "repos": 0,  # 0 means fetch from GitHub
        "followers": 0,  # 0 means fetch from GitHub
        "years_exp": 0,  # Removed from display
    },
    "max_projects_display": 6,
    "hide_forked_repos": True,
    "content": {
        "about_bio": "Motivated software developer with expertise in Python, web development, and databases. Passionate about AI and backend development. I build efficient, scalable solutions and love exploring new technologies.",
        "about_role": "Software Developer",
        "skills": {
            "languages": ["Python", "C", "Java", "PHP"],
            "web": ["HTML5", "CSS3", "JavaScript", "Bootstrap"],
            "databases": ["MySQL", "PostgreSQL", "MongoDB"],
            "frameworks": ["Django", "FastAPI", "Streamlit"],
            "tools": ["Git", "GitHub", "Docker", "AWS", "Postman", "Power BI"],
        },
        "certificates": [
            {"title": "Data Science", "issuer": "Cisco"},
        ],
    },
    "last_updated": datetime.now().isoformat(),
}

DEFAULT_SELECTED_PROJECTS = {
    "enabled": True,
    "selected_repos": [],  # List of repo names to display
    "excluded_repos": [],  # List of repo names to hide
    "last_updated": datetime.now().isoformat(),
}


def hash_password(password: str) -> str:
    """Hash admin password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_admin_credentials(password: str = "admin123"):
    """Initialize admin credentials (one-time setup)."""
    if CREDENTIALS_FILE.exists():
        console.log("[yellow]Admin credentials already exist[/yellow]")
        return

    hashed = hash_password(password)
    CREDENTIALS_FILE.write_text(hashed)
    CREDENTIALS_FILE.chmod(0o600)  # Read-only for owner
    console.log("[green]✓ Admin credentials initialized[/green]")
    console.log(f"[yellow]Default password: admin123 — CHANGE THIS IMMEDIATELY[/yellow]")


def verify_admin_password(password: str) -> bool:
    """Verify admin password."""
    if not CREDENTIALS_FILE.exists():
        init_admin_credentials()

    stored_hash = CREDENTIALS_FILE.read_text().strip()
    return hash_password(password) == stored_hash


def load_settings() -> Dict[str, Any]:
    """Load admin settings from file, create if not exists."""
    if ADMIN_FILE.exists():
        try:
            return json.loads(ADMIN_FILE.read_text())
        except json.JSONDecodeError:
            console.log("[red]Error reading settings, using defaults[/red]")
            return DEFAULT_SETTINGS.copy()

    # Create default settings
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> bool:
    """Save admin settings to file."""
    try:
        settings["last_updated"] = datetime.now().isoformat()
        ADMIN_FILE.write_text(json.dumps(settings, indent=2))
        console.log("[green]✓ Settings saved[/green]")
        return True
    except Exception as e:
        console.log(f"[red]✗ Failed to save settings: {e}[/red]")
        return False


def load_selected_projects() -> Dict[str, Any]:
    """Load selected projects configuration."""
    if PROJECTS_FILE.exists():
        try:
            return json.loads(PROJECTS_FILE.read_text())
        except json.JSONDecodeError:
            console.log("[red]Error reading projects, using defaults[/red]")
            return DEFAULT_SELECTED_PROJECTS.copy()

    # Create default
    save_selected_projects(DEFAULT_SELECTED_PROJECTS)
    return DEFAULT_SELECTED_PROJECTS.copy()


def save_selected_projects(projects: Dict[str, Any]) -> bool:
    """Save selected projects configuration."""
    try:
        projects["last_updated"] = datetime.now().isoformat()
        PROJECTS_FILE.write_text(json.dumps(projects, indent=2))
        console.log("[green]✓ Projects configuration saved[/green]")
        return True
    except Exception as e:
        console.log(f"[red]✗ Failed to save projects: {e}[/red]")
        return False


def update_settings(key: str, value: Any) -> bool:
    """Update a single setting."""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


def get_setting(key: str, default: Any = None) -> Any:
    """Get a single setting."""
    settings = load_settings()
    return settings.get(key, default)


def should_show_events() -> bool:
    """Check if Activities & Events should be shown."""
    return get_setting("show_events", False)


def get_display_stats() -> Dict[str, int]:
    """Get configured display stats."""
    return get_setting("display_stats", DEFAULT_SETTINGS["display_stats"])


def add_excluded_repo(repo_name: str) -> bool:
    """Add a repo to excluded list (hide it)."""
    projects = load_selected_projects()
    if repo_name not in projects["excluded_repos"]:
        projects["excluded_repos"].append(repo_name)
    return save_selected_projects(projects)


def remove_excluded_repo(repo_name: str) -> bool:
    """Remove a repo from excluded list (show it)."""
    projects = load_selected_projects()
    if repo_name in projects["excluded_repos"]:
        projects["excluded_repos"].remove(repo_name)
    return save_selected_projects(projects)


def get_excluded_repos() -> List[str]:
    """Get list of excluded repo names."""
    projects = load_selected_projects()
    return projects.get("excluded_repos", [])


def filter_repos_by_admin(repos: List) -> List:
    """Filter repos based on admin excluded list."""
    excluded = get_excluded_repos()
    filtered = []
    for repo in repos:
        # Handle both Pydantic models and dictionaries
        repo_name = repo.name if hasattr(repo, 'name') else repo.get("name")
        if repo_name not in excluded:
            filtered.append(repo)
    return filtered


# ============ CONTENT EDITING ============

def get_content() -> Dict[str, Any]:
    """Get all editable content (about, skills, certificates)."""
    settings = load_settings()
    return settings.get("content", DEFAULT_SETTINGS["content"].copy())


def update_about(bio: str, role: str) -> bool:
    """Update About section content."""
    settings = load_settings()
    if "content" not in settings:
        settings["content"] = DEFAULT_SETTINGS["content"].copy()
    settings["content"]["about_bio"] = bio
    settings["content"]["about_role"] = role
    return save_settings(settings)


def update_skills(skills: Dict[str, List[str]]) -> bool:
    """Update skills content."""
    settings = load_settings()
    if "content" not in settings:
        settings["content"] = DEFAULT_SETTINGS["content"].copy()
    settings["content"]["skills"] = skills
    return save_settings(settings)


def update_certificates(certificates: List[Dict[str, str]]) -> bool:
    """Update certificates/education content."""
    settings = load_settings()
    if "content" not in settings:
        settings["content"] = DEFAULT_SETTINGS["content"].copy()
    settings["content"]["certificates"] = certificates
    return save_settings(settings)


# Initialize on import
if not CREDENTIALS_FILE.exists():
    init_admin_credentials()
