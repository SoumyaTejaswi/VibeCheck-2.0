"""Command-line runner for the Music Recommender Simulation."""

import argparse
import logging
from pathlib import Path

from src.recommender import filter_eligible_songs, load_songs, recommend_songs
from src.reliability import (
    catalog_warnings,
    validate_preferences,
    verify_recommendations,
)


LOGGER = logging.getLogger(__name__)
CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "songs.csv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recommend songs based on your listening preferences."
    )
    parser.add_argument("--genre", default="pop", help="Favorite genre")
    parser.add_argument("--mood", default="happy", help="Favorite mood")
    parser.add_argument(
        "--energy", type=float, default=0.8, help="Target energy from 0 to 1"
    )
    parser.add_argument(
        "--acoustic",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Prefer acoustic tracks",
    )
    parser.add_argument(
        "--exclude-explicit",
        action="store_true",
        help="Exclude tracks marked explicit",
    )
    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of recommendations"
    )
    args = parser.parse_args()

    # Reject invalid preferences before loading the catalog or ranking songs.
    try:
        genre, mood = validate_preferences(
            args.genre, args.mood, args.energy, args.top_k
        )
    except ValueError as error:
        parser.error(str(error))

    user_prefs = {
        "favorite_genre": genre,
        "favorite_mood": mood,
        "target_energy": args.energy,
        "likes_acoustic": args.acoustic,
        "allow_explicit": not args.exclude_explicit,
    }

    try:
        songs = load_songs(str(CATALOG_PATH))
    except (OSError, ValueError, KeyError) as error:
        LOGGER.error("Could not load the song catalog: %s", error)
        return 1

    # Coverage and verification use the same eligibility rule as ranking.
    eligible_songs = filter_eligible_songs(songs, user_prefs["allow_explicit"])
    if not eligible_songs:
        print("No eligible songs are available for this request.")
        return 0

    warnings = catalog_warnings(genre, mood, eligible_songs)
    recommendations = recommend_songs(user_prefs, songs, k=args.top_k)

    # Keep the playlist hidden until all output checks pass.
    try:
        verify_recommendations(recommendations, eligible_songs, args.top_k)
    except ValueError as error:
        LOGGER.error("Recommendation verification failed: %s", error)
        return 1

    for warning in warnings:
        print(f"Warning: {warning}")

    print("\nTop Recommendations")
    print("=" * 40)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} (match score: {score:.2f})")

        if explanation:
            for reason in explanation.split("; "):
                print(f"   - {reason}")
        else:
            print("   - No strong matches with your preferences")

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    raise SystemExit(main())