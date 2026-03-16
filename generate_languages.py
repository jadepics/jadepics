import os
import requests
import os
import requests

USERNAME = os.getenv("GITHUB_USERNAME", "jadepics")
TOKEN = os.getenv("GITHUB_TOKEN")
README_FILE = "README.md"

headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def get_repos(username):
    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{jadepics}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_languages(languages_url):
    response = requests.get(languages_url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()

def aggregate_languages(username):
    repos = get_repos(username)
    totals = {}

    for repo in repos:
        # Salta fork e repo archiviati, se vuoi un profilo più pulito
        if repo.get("fork") or repo.get("archived"):
            continue

        languages = get_languages(repo["languages_url"])
        for lang, value in languages.items():
            totals[lang] = totals.get(lang, 0) + value

    return totals

def build_markdown(languages):
    if not languages:
        return "- Nessun linguaggio trovato"

    total_bytes = sum(languages.values())
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)

    lines = []
    for lang, value in sorted_langs[:8]:
        percentage = (value / total_bytes) * 100 if total_bytes else 0
        lines.append(f"- **{lang}**: {percentage:.1f}%")

    return "\n".join(lines)

def update_readme(content):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!-- LANGUAGES_START -->"
    end_marker = "<!-- LANGUAGES_END -->"

    start = readme.find(start_marker)
    end = readme.find(end_marker)

    if start == -1 or end == -1:
        raise ValueError("Marker LANGUAGES_START o LANGUAGES_END non trovati nel README.md")

    new_section = f"{start_marker}\n{content}\n{end_marker}"
    updated = readme[:start] + new_section + readme[end + len(end_marker):]

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    languages = aggregate_languages(USERNAME)
    markdown = build_markdown(languages)
    update_readme(markdown)
    print("README aggiornato correttamente.")

if __name__ == "__main__":
    main()
