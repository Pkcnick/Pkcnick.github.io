import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone


AUTHOR_ID = "aTCilz0AAAAJ"
PROFILE_URL = "https://scholar.google.com/citations?hl=en&user=aTCilz0AAAAJ"
OUTPUT_FILE = "citations.json"


def extract_metric(cited_by, metric_name):
    """
    SerpApi may return citation metrics in slightly different structures.
    This function tries to safely extract:
    citations, h_index, i10_index.
    """
    table = cited_by.get("table", [])

    for row in table:
        if metric_name in row:
            value = row[metric_name]

            if isinstance(value, dict):
                return value.get("all") or value.get("total") or 0

            return value

    return 0


def main():
    api_key = os.environ.get("SERPAPI_KEY")

    if not api_key:
        print("Missing SERPAPI_KEY environment variable.")
        sys.exit(1)

    params = {
        "engine": "google_scholar_author",
        "author_id": AUTHOR_ID,
        "hl": "en",
        "api_key": api_key,
    }

    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print(f"Failed to fetch Scholar data: {error}")
        sys.exit(1)

    cited_by = data.get("cited_by", {})

    citations = extract_metric(cited_by, "citations")
    h_index = extract_metric(cited_by, "h_index")
    i10_index = extract_metric(cited_by, "i10_index")

    output = {
        "source": "Google Scholar via SerpApi",
        "profile_url": PROFILE_URL,
        "citations": citations,
        "h_index": h_index,
        "i10_index": i10_index,
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
