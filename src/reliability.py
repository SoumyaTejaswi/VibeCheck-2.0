"""Input validation and output verification for the music recommender."""

from math import isfinite


def normalize_label(value: str) -> str:
    """Treat labels such as ' Pop ' and 'pop' as equivalent."""
    return value.strip().casefold()


def validate_preferences(
    genre: str, mood: str, energy: float, top_k: int
) -> tuple[str, str]:
    """Return normalized labels or raise an error the CLI can display."""
    genre = normalize_label(genre)
    mood = normalize_label(mood)

    if not genre:
        raise ValueError("--genre cannot be blank.")
    if not mood:
        raise ValueError("--mood cannot be blank.")
    if not isfinite(energy) or not 0 <= energy <= 1:
        raise ValueError("--energy must be a finite number between 0 and 1.")
    if top_k < 1:
        raise ValueError("--top-k must be at least 1.")

    return genre, mood


def catalog_warnings(
    genre: str, mood: str, eligible_songs: list[dict]
) -> list[str]:
    """Check genre and mood coverage after applying the content filter."""
    available_genres = {normalize_label(song["genre"]) for song in eligible_songs}
    available_moods = {normalize_label(song["mood"]) for song in eligible_songs}
    warnings = []

    if genre not in available_genres:
        warnings.append(f"No eligible songs match the genre '{genre}'.")
    if mood not in available_moods:
        warnings.append(f"No eligible songs match the mood '{mood}'.")
    if warnings:
        warnings.append("Showing partial matches based on your other preferences.")

    return warnings


def verify_recommendations(
    recommendations: list[tuple[dict, float, str]],
    eligible_songs: list[dict],
    top_k: int,
) -> None:
    """Raise an error if the ranked playlist fails a reliability check."""
    expected_count = min(top_k, len(eligible_songs))
    if len(recommendations) != expected_count:
        raise ValueError(
            f"Expected {expected_count} recommendations, "
            f"received {len(recommendations)}."
        )

    eligible_ids = {song["id"] for song in eligible_songs}
    seen_ids = set()
    previous_score = float("inf")

    for song, score, _ in recommendations:
        song_id = song["id"]

        if song_id not in eligible_ids:
            raise ValueError(f"Song ID {song_id} is outside the eligible catalog.")
        if song_id in seen_ids:
            raise ValueError(f"Song ID {song_id} appears more than once.")
        if not isfinite(score):
            raise ValueError(f"Song ID {song_id} has a non-finite score.")
        if score > previous_score:
            raise ValueError("Recommendations are out of score order.")

        # Equal scores are allowed. The recommender handles tie-breaking.
        seen_ids.add(song_id)
        previous_score = score