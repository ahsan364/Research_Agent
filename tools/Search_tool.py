import os
import requests
from langchain.tools import tool

SERPER_URL = "https://google.serper.dev/search"
MAX_SEARCHES = 5

# Simple in-memory counter, reset per process run via reset_search_count()
_search_count = {"count": 0}


def reset_search_count():
    _search_count["count"] = 0


@tool("web_search", return_direct=False)
def web_search(query: str) -> str:
    """
    Search the web for a given query using Serper (Google Search API).
    Returns a formatted string of the top organic results (title, snippet, link).
    Use this to find current, factual, or niche information you don't already know.
    You have a limited number of searches — use them on distinct, specific queries.
    """
    if _search_count["count"] >= MAX_SEARCHES:
        return (
            "SEARCH LIMIT REACHED. You have used all available searches. "
            "Do NOT call web_search again. You must now write the final Markdown "
            "report using only the information you have already gathered."
        )

    _search_count["count"] += 1

    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY not set."

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": 8}

    try:
        response = requests.post(SERPER_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Search failed: {e}"

    data = response.json()
    results = data.get("organic", [])

    if not results:
        return f"No results found. ({MAX_SEARCHES - _search_count['count']} searches remaining.)"

    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        formatted.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")

    remaining = MAX_SEARCHES - _search_count["count"]
    formatted.append(f"\n({remaining} searches remaining — use them wisely.)")

    return "\n\n".join(formatted)