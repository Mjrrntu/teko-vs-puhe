import json
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path(
    "data/raw/sali_aanestys_edustaja_13259_normalized.json"
)


def load_votes():
    with INPUT_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_vote(vote):
    vote = vote.strip().lower()

    mapping = {
        "jaa": "jaa",
        "ei": "ei",
        "tyhjä": "tyhjä",
        "poissa": "poissa",
    }

    return mapping.get(vote, vote)


def main():
    rows = load_votes()

    party_counts = defaultdict(lambda: defaultdict(int))

    for row in rows:
        party = row["EdustajaRyhmaLyhenne"].strip().upper()
        vote = normalize_vote(row["EdustajaAanestys"])

        party_counts[party][vote] += 1

    print("# Puoluekohtainen äänijakauma")
    print()

    for party in sorted(party_counts.keys()):
        counts = party_counts[party]

        print(f"## {party}")
        print(f"JAA:    {counts['jaa']}")
        print(f"EI:     {counts['ei']}")
        print(f"TYHJÄ:  {counts['tyhjä']}")
        print(f"POISSA: {counts['poissa']}")
        print()


if __name__ == "__main__":
    main()
