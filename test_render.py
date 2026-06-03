#!/usr/bin/env python
"""Test template rendering with admin settings."""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from models import GitHubProfile

BASE_DIR = Path(".")
jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")), autoescape=True)
template = jinja_env.get_template("index.html")

# Create dummy data
dummy_profile = GitHubProfile(
    login="test",
    name="Test User",
    avatar_url="https://example.com/avatar.jpg",
    bio="Test bio",
    public_repos=10,
    followers=5,
    following=3,
    html_url="https://github.com/test"
)

display_stats = {"repos": 0, "followers": 0, "years_exp": 2}
show_events = False

try:
    content = template.render(
        profile=dummy_profile,
        display_stats=display_stats,
        show_events=show_events,
        repos=[],
        portfolio=None,
        request=None,
        last_updated=None
    )
    print("✓ Template rendered OK")
    # Print a snippet to verify
    if "data-target=" in content:
        print("✓ data-target attributes found in rendered output")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
