import json
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://avoindata.eduskunta.fi/api/v1/tables"
OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_table(table_name, page=0, per_page=100, column_name=None, column_value=None):
    params = {
        "page": page,
        "perPage": per_page,
    }

    if column_name and column_value:
        params["columnName"] = column_name
        params["columnValue"] = column_value

    url = f"{BASE_URL}/{table_name}/rows?{urllib.parse.urlencode(params)}"
    print(f"Fetching: {url}")

    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print()
        print(f"HTTP error: {e.code}")
        print(error_body)
        print()
        return {
            "error": True,
            "status": e.code,
            "url": url,
            "body": error_body,
        }


def fetch_all_rows(table_name, column_name=None, column_value=None, per_page=100):
    all_rows = []
    page = 0
    last_payload = None

    while True:
        payload = fetch_table(
            table_name=table_name,
            page=page,
            per_page=per_page,
            column_name=column_name,
            column_value=column_value,
        )

        if payload.get("error"):
            return payload, []

        rows = rows_to_dicts(payload)
        all_rows.extend(rows)
        last_payload = payload

        if not payload.get("hasMore"):
            break

        page += 1

    return last_payload, all_rows


def rows_to_dicts(payload):
    if payload.get("error"):
        return []

    columns = payload["columnNames"]

    return [
        dict(zip(columns, row))
        for row in payload["rowData"]
    ]


def save_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved: {path}")


def main():
    votes_payload = fetch_table("SaliDBAanestys", page=0, per_page=10)
    save_json(OUT_DIR / "sali_aanestys_sample_raw.json", votes_payload)

    votes = rows_to_dicts(votes_payload)
    save_json(OUT_DIR / "sali_aanestys_sample_normalized.json", votes)

    if not votes:
        print("No vote rows found.")
        return

    first_vote = votes[0]

    print()
    print("First normalized vote:")
    print(json.dumps(first_vote, indent=2, ensure_ascii=False))

    vote_id = first_vote.get("AanestysId")

    if not vote_id:
        print("Could not detect AanestysId from first vote.")
        return

    print()
    print(f"Fetching all member votes for AanestysId={vote_id}")

    member_votes_payload, member_votes = fetch_all_rows(
        "SaliDBAanestysEdustaja",
        column_name="AanestysId",
        column_value=vote_id,
        per_page=100,
    )

    save_json(
        OUT_DIR / f"sali_aanestys_edustaja_{vote_id}_last_raw_page.json",
        member_votes_payload,
    )

    save_json(
        OUT_DIR / f"sali_aanestys_edustaja_{vote_id}_normalized.json",
        member_votes,
    )

    if member_votes:
        print()
        print(f"Fetched {len(member_votes)} member votes for AanestysId={vote_id}")
        print()
        print("First member vote:")
        print(json.dumps(member_votes[0], indent=2, ensure_ascii=False))
    else:
        print()
        print("Could not fetch member votes.")


if __name__ == "__main__":
    main()
