#!/usr/bin/env python
"""Test the home route rendering."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock

# Set up the environment
import sys
sys.path.insert(0, str(Path.cwd()))

from main import home, get_portfolio_data
from admin_storage import (
    get_display_stats, should_show_events, get_excluded_repos,
    filter_repos_by_admin
)
from models import PortfolioData, GitHubProfile

# Mock request
mock_request = MagicMock()
mock_request.url = "http://localhost:8000/"

async def test_home():
    try:
        print("Getting portfolio data...")
        portfolio = get_portfolio_data()
        print(f"✓ Portfolio data retrieved: {len(portfolio.repos)} repos")
        
        print("Getting display stats...")
        display_stats = get_display_stats()
        print(f"✓ Display stats: {display_stats}")
        
        print("Getting show_events...")
        show_events = should_show_events()
        print(f"✓ Show events: {show_events}")
        
        print("Getting excluded repos...")
        excluded_repos = get_excluded_repos()
        print(f"✓ Excluded repos: {excluded_repos}")
        
        print("Filtering repos...")
        filtered_repos = filter_repos_by_admin(portfolio.repos)
        print(f"✓ Filtered repos: {len(filtered_repos)}")
        
        print("\nCalling home route...")
        response = await home(mock_request)
        print(f"✓ Home route returned successfully ({len(response.body)} bytes)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_home())
