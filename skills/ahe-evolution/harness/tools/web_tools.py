"""Web search and fetch tools. Stub implementations — real API calls need API keys."""


def web_search(query: str) -> str:
    """Search the web. Returns formatted search results.
    Requires SERPER_API_KEY or equivalent to be set in environment."""
    import os
    import urllib.request
    import json

    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return (
            "Web search unavailable: SERPER_API_KEY not set. "
            "Provide a search query and I will note that web access is needed."
        )

    try:
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=json.dumps({"q": query}).encode("utf-8"),
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return f"Web search failed: {e}"

    results = []
    for item in data.get("organic", [])[:10]:
        results.append(f"- [{item.get('title', '?')}]({item.get('link', '#')})")
        snippet = item.get("snippet", "")
        if snippet:
            results.append(f"  {snippet[:200]}")
    return "\n".join(results) if results else "No results found."
