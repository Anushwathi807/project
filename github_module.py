def extract_username(user_input):
    user_input = user_input.strip()
    if "github.com" in user_input:
        # e.g. https://github.com/octocat or https://github.com/octocat/
        parts = user_input.rstrip('/').split('/')
        return parts[-1]
    return user_input

import requests

def get_github_profile(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    return {
        "name": data.get("name"),
        "bio": data.get("bio"),
        "followers": data.get("followers"),
        "public_repos": data.get("public_repos")
    }

def get_github_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    repos = response.json()
    repo_list = []
    for repo in repos:
        repo_list.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at")
        })
    return repo_list
def aggregate_languages(repo_list):
    language_counts = {}
    for repo in repo_list:
        lang = repo.get("language")
        if lang:  # skip repos with no language (e.g., None)
            language_counts[lang] = language_counts.get(lang, 0) + 1
    return language_counts

def get_github_summary(user_input):
    username = extract_username(user_input)
    profile = get_github_profile(username)

    if profile is None:
        return {"error": f"GitHub user '{username}' not found"}

    repos = get_github_repos(username)      # ✅ correct
    languages = aggregate_languages(repos)   # ✅ correct — passing the list we just got

    return {
        "username": username,
        "profile": profile,
        "repos": repos,        # ✅ correct — dict key "repos" maps to our local variable repos
        "languages": languages
    }