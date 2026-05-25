import json
from collections import defaultdict
from pathlib import Path

DATA_PATH = Path("data/relevant_votes.json")


def load_votes():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_vote(value):
    if value is None:
        return "tuntematon"

    return str(value).strip().lower()


def analyze(votes):
    stats = defaultdict(
        lambda: {
            "supporting": 0,
            "opposing": 0,
            "neutral": 0,
            "unknown": 0,
            "evidence": [],
        }
    )

    for vote in votes:
        expected_vote = normalize_vote(vote["expected_vote"])

        for party, party_vote_raw in vote["party_votes"].items():
            party_vote = normalize_vote(party_vote_raw)

            if party_vote == expected_vote:
                stats[party]["supporting"] += 1
                stance = "tuki teemaa edistävää kantaa"
            elif party_vote in ["jaa", "ei"]:
                stats[party]["opposing"] += 1
                stance = "äänesti teemaa edistävää kantaa vastaan"
            elif party_vote in ["tyhjä", "poissa"]:
                stats[party]["neutral"] += 1
                stance = "ei ottanut selkeää kantaa"
            else:
                stats[party]["unknown"] += 1
                stance = "tuntematon kanta"

            stats[party]["evidence"].append(
                {
                    "id": vote["id"],
                    "date": vote["date"],
                    "title": vote["title"],
                    "theme": vote["theme"],
                    "public_line": vote.get("public_line", "Ei määritelty"),
                    "party_vote": party_vote,
                    "expected_vote": expected_vote,
                    "stance": stance,
                    "reason": vote["reason"],
                    "source_url": vote["source_url"],
                }
            )

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


def voting_line(supporting, opposing):
    total = supporting + opposing

    if total == 0:
        return "Ei selkeää äänestyslinjaa"

    ratio = supporting / total

    if ratio >= 0.75:
        return "Usein puolesta"
    if ratio >= 0.45:
        return "Vaihtelee"
    return "Usein vastaan"


def print_summary(stats):
    print()
    print("# Kysymys: tuetaanko pienituloisia?")
    print()
    print("Analyysi perustuu käsin valittuihin ja perusteltuihin eduskunnan äänestyksiin.")
    print("Huom: POC-versio. Yhteenveto perustuu pieneen käsin valittuun aineistoon, eikä sitä pidä tulkita kattavana puoluearviona.")
    print()
    print("| Puolue | Julkinen linja | Äänestyslinja | Konsistenssi | Todisteet |")
    print("|---|---|---|---|---|")

    for party, s in sorted(stats.items()):
        supporting = s["supporting"]
        opposing = s["opposing"]
        neutral = s["neutral"]

        public_line = s["evidence"][0]["public_line"]
        line = voting_line(supporting, opposing)
        consistency = consistency_label(supporting, opposing)

        print(
            f"| {party} | "
            f"{public_line} | "
            f"{line} ({supporting} puolesta, {opposing} vastaan, {neutral} ei selkeää kantaa) | "
            f"{consistency} | "
            f"Katso alla |"
        )


def print_evidence(stats):
    print()
    print("## Todisteet")
    print()

    for party, s in sorted(stats.items()):
        print(f"### {party}")
        print()

        for ev in s["evidence"]:
            print(f"- {ev['date']}: {ev['title']}")
            print(f"  - Teema: {ev['theme']}")
            print(f"  - Puolueen ääni: {ev['party_vote']}")
            print(f"  - Teemaa edistävä kanta: {ev['expected_vote']}")
            print(f"  - Tulkinta: {ev['stance']}")
            print(f"  - Perustelu: {ev['reason']}")
            print(f"  - Lähde: {ev['source_url']}")
            print()


def main():
    votes = load_votes()
    stats = analyze(votes)

    print_summary(stats)
    print_evidence(stats)


if __name__ == "__main__":
    main()
