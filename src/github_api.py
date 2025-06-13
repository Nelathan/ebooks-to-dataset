"""
github_api.py

Handles fetching and filtering Standard Ebooks repositories from GitHub.
"""

import os
import requests

GITHUB_ORG = "standardebooks"
GITHUB_API = f"https://api.github.com/orgs/{GITHUB_ORG}/repos?per_page=100&type=public"

def fetch_repo_list():
    """
    Use GitHub API to fetch all repos from standardebooks org.
    Returns a list of dicts with: name, link, updated_at, clone_url, default_branch.
    Skips meta/tool repos.
    """
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    repos = []
    page = 1

    while True:
        url = f"{GITHUB_API}&page={page}"
        resp = requests.get(url, headers=headers)
        print(f"GitHub API page {page} status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"GitHub API error body: {resp.text}")
            break
        data = resp.json()
        if not data:
            print(f"No more data on page {page}.")
            break

        for repo in data:
            # Heuristic: HTML book repos have "standardebooks" as owner and are not meta/tools
            if repo["name"].startswith("standardebooks-") or repo["name"] in ["site", "tools", "se-builder"]:
                continue
            repos.append({
                "name": repo["name"],
                "link": repo["html_url"],
                "updated_at": repo["updated_at"],
                "clone_url": repo["clone_url"],
                "default_branch": repo["default_branch"],
            })

        # If we got fewer than 100 repos, we've reached the end
        if len(data) < 100:
            break
        page += 1

    print(f"Fetched {len(repos)} repos from GitHub API across {page} pages.")
    return repos

def filter_updated_repos(new_list, old_list_path):
    """
    Compare new_list to old_list (if exists).
    Drop repos where updated_date is unchanged.
    Keep repos that are new or have a newer updated_date.
    """
    import os
    import json
    if not os.path.exists(old_list_path):
        return new_list
    with open(old_list_path, "r") as f:
        old_list = {r["name"]: r for r in json.load(f)}
    filtered = []
    for repo in new_list:
        old = old_list.get(repo["name"])
        if not old or repo["updated_at"] > old["updated_at"]:
            filtered.append(repo)
    return filtered
