import json
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path("data/poc_votes.json")


def load_votes():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def analyze(votes):
    stats = defaultdict(lambda: {"supporting": 0, "opposing": 0, "unknown": 0, "evidence": []})

    for vote in votes:
        expected = vote["expected_vote"]

        for party, party_vote in vote["party_votes"].items():
            if party_vote == expected:
                stats[party]["supporting"] += 1
                stance = "tuki pienituloisia edistävää kantaa"
            elif party_vote in ["jaa", "ei"]:
                stats[party]["opposing"] += 1
                stance = "äänesti pienituloisia edistävää kantaa vastaan"
            else:
                stats[party]["unknown"] += 1
                stance = "ei selkeää kantaa"

            stats[party]["evidence"].append({
                "date": vote["date"],
                "title": vote["title"],
                "party_vote": party_vote,
                "expected_vote": expected,
                "stance": stance,
                "reason": vote["reason"],
                "source_url": vote["source_url"],
            })

    return stats


def consistency_label(supporting, opposing):
    total = supporting + opposing
    if total == 0:
        return "Ei dataa"

    ratio = supporting / total

    if ratio >= 0.75:
        return "Korkea"
    if ratio >= 0.45:
        return "Keskitaso"
    return "Matala"


def main():
    votes = load_votes()
    stats = analyze(votes)

    print("# teko-vs-puhe POC 0.1")
    print()
    print("| Puolue | Äänestyslinja | Konsistenssi |")
    print("|---|---|---|")

    for party, s in sorted(stats.items()):
        supporting = s["supporting"]
        opposing = s["opposing"]
        label = consistency_label(supporting, opposing)

        print(
            f"| {party} | "
            f"{supporting} kertaa puolesta, {opposing} kertaa vastaan | "
            f"{label} |"
        )


        print()
    print("## Todisteet")
    print()

    for party, s in sorted(stats.items()):
        print(f"### {party}")
        print()

        for ev in s["evidence"]:
            print(f"- {ev['date']}: {ev['title']}")
            print(f"  - Äänesti: {ev['party_vote']}")
            print(f"  - Odotettu pienituloisia tukeva kanta: {ev['expected_vote']}")
            print(f"  - Tulkinta: {ev['stance']}")
            print(f"  - Perustelu: {ev['reason']}")
            print(f"  - Lähde: {ev['source_url']}")
            print()


if __name__ == "__main__":
    main()
