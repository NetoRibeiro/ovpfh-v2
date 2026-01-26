#!/usr/bin/env python3
"""
Update Match Scores
Reads matches.json and updates null scores using data from resultados files.
Only updates scores for matches with status "finished" in resultados.

Run daily at 05:00 AM via Windows Task Scheduler.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Base directories
BASE_DIR = Path(__file__).parent.parent
MATCHES_FILE = BASE_DIR / "data" / "matches.json"
RESULTADOS_DIR = BASE_DIR / "resultados"

# Team name normalization mapping
# Maps resultados team names to matches.json team names
TEAM_NAME_MAP = {
    # Paulistão teams
    "botafogo-sp": "botafogorp",
    "primavera-sp": "esporteclubeprimavera",
    "noroeste": "esporteclubenoroeste",
    "ponte-preta": "pontepreta",
    "sao-bernardo-fc": "saobernardofc",
    "santos-fc": "santos",
    "corinthians-sao-paulo": "corinthians",
    "sao-paulo-fc": "saopaulo",
    "a-portuguesa-d": "portuguesa",
    "velo-clube": "veloclube",
    "guarani-campinas": "guarani",
    "mirassol": "mirassol",
    "bragantino": "bragantino",
    "novorizontino": "novorizontino",
    "palmeiras": "palmeiras",
    "capivariano": "capivariano",
    # Carioca teams
    "flamengo-rio-janeiro": "flamengo",
    "fluminense-rio-janeiro": "fluminense",
    "botafogo-rio-janeiro": "botafogo",
    "vasco-da-gama": "vasco",
    "cfrj-marica": "marica",
    "volta-redonda": "voltaredonda",
    "madureira-rj": "madureira",
    "sampaio-correa-rj": "sampaiocorrea",
    "boavista-br": "boavista",
    "nova-iguacu": "novaiguacu",
}


def normalize_team_name(name):
    """Normalize team name for matching."""
    # First check if there's a direct mapping
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]

    # Otherwise, normalize by removing hyphens and converting to lowercase
    normalized = name.lower().replace("-", "").replace(" ", "")
    return normalized


def load_matches():
    """Load matches from matches.json."""
    try:
        with open(MATCHES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading matches.json: {e}")
        return None


def save_matches(data):
    """Save matches to matches.json."""
    try:
        with open(MATCHES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving matches.json: {e}")
        return False


def load_resultados():
    """Load all resultados files and extract finished matches."""
    finished_matches = []

    if not RESULTADOS_DIR.exists():
        print(f"Resultados directory not found: {RESULTADOS_DIR}")
        return finished_matches

    for json_file in RESULTADOS_DIR.glob("*_resultados.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            matches = data.get("matches", [])
            for match in matches:
                # Only consider finished matches
                if match.get("status") == "finished":
                    score = match.get("score", {})
                    if score.get("home") is not None and score.get("away") is not None:
                        finished_matches.append({
                            "homeTeam": normalize_team_name(match.get("homeTeam", "")),
                            "awayTeam": normalize_team_name(match.get("awayTeam", "")),
                            "score": score,
                            "matchDate": match.get("matchDate"),
                            "source": json_file.name
                        })

            print(f"Loaded {len(matches)} matches from {json_file.name}")

        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")

    return finished_matches


def find_matching_result(match, finished_results):
    """Find a matching result for a given match."""
    home_team = normalize_team_name(match.get("homeTeam", ""))
    away_team = normalize_team_name(match.get("awayTeam", ""))

    for result in finished_results:
        if result["homeTeam"] == home_team and result["awayTeam"] == away_team:
            return result

    return None


def update_scores():
    """Main function to update null scores in matches.json."""
    print("=" * 60)
    print(f"Score Update Job - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Load matches
    matches_data = load_matches()
    if not matches_data:
        print("Failed to load matches.json")
        return

    # Load finished results from resultados
    finished_results = load_resultados()
    print(f"\nFound {len(finished_results)} finished matches in resultados")
    print()

    # Find matches with null scores
    matches_list = matches_data.get("matches", [])
    updated_count = 0

    for match in matches_list:
        score = match.get("score", {})

        # Check if score is null
        if score.get("home") is None or score.get("away") is None:
            # Try to find matching result
            result = find_matching_result(match, finished_results)

            if result:
                # Update the score
                match["score"] = result["score"]
                match["status"] = "finished"
                updated_count += 1
                print(f"Updated: {match.get('homeTeam')} vs {match.get('awayTeam')} -> {result['score']['home']}-{result['score']['away']}")

    # Save if there were updates
    if updated_count > 0:
        if save_matches(matches_data):
            print(f"\nSaved {updated_count} score updates to matches.json")
        else:
            print("\nFailed to save updates")
    else:
        print("\nNo scores to update")

    print()
    print("=" * 60)
    print("Job completed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        update_scores()
    except KeyboardInterrupt:
        print("\n\nUpdate interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise
