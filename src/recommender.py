"""Load, score, and rank songs for the music recommender."""

import csv
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from src.reliability import normalize_label


@dataclass
class Song:
    """A song and its catalog metadata."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 0
    release_decade: str = ""
    detailed_mood_tags: List[str] = field(default_factory=list)
    explicit: bool = False
    language: str = ""
    instrumentalness: float = 0.0


@dataclass
class UserProfile:
    """A listener's required and optional preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    favorite_decade: Optional[str] = None
    prefers_popular: Optional[bool] = None
    mood_keywords: List[str] = field(default_factory=list)
    favorite_language: Optional[str] = None
    prefers_vocals: Optional[bool] = None
    allow_explicit: bool = True


class Recommender:
    """Expose the same scoring and ranking logic through the Song class."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Run the same ranking function the CLI uses, then return Song objects.
        songs_by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(
            asdict(user),
            [asdict(song) for song in self.songs],
            k=k,
        )
        return [songs_by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the song catalog and convert CSV text to the types scoring expects."""
    songs = []
    with open(csv_path, newline="") as catalog_file:
        reader = csv.DictReader(catalog_file)
        for row in reader:
            tags = row["detailed_mood_tags"]
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    "popularity": int(row["popularity"]),
                    "release_decade": row["release_decade"],
                    "detailed_mood_tags": tags.split("|") if tags else [],
                    "explicit": row["explicit"].strip().lower() == "true",
                    "language": row["language"],
                    "instrumentalness": float(row["instrumentalness"]),
                }
            )
    return songs


# The four core preferences contribute up to 5.5 points.
GENRE_WEIGHT = 1.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 2.0
ACOUSTIC_WEIGHT = 1.0

# The optional preferences contribute up to 3.5 additional points.
DECADE_WEIGHT = 1.0
POPULARITY_WEIGHT = 0.5
MOOD_TAG_WEIGHT = 1.0
LANGUAGE_WEIGHT = 0.5
INSTRUMENTAL_WEIGHT = 0.5


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return one song's match score and the reasons behind it."""
    reasons = []

    # Normalize both sides so equivalent labels receive the same score.
    genre_matches = normalize_label(song["genre"]) == normalize_label(
        user_prefs["favorite_genre"]
    )
    genre_match = GENRE_WEIGHT if genre_matches else 0.0
    if genre_match:
        reasons.append(f"Matches your favorite genre ({song['genre']})")

    mood_matches = normalize_label(song["mood"]) == normalize_label(
        user_prefs["favorite_mood"]
    )
    mood_match = MOOD_WEIGHT if mood_matches else 0.0
    if mood_match:
        reasons.append(f"Matches your favorite mood ({song['mood']})")

    # Use unweighted closeness to decide whether the energy match is strong.
    energy_gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_raw_closeness = max(0, 1 - energy_gap)
    energy_closeness = ENERGY_WEIGHT * energy_raw_closeness
    if energy_raw_closeness >= 0.8:
        reasons.append("Energy closely matches your target")

    if user_prefs["likes_acoustic"]:
        acoustic_raw = song["acousticness"]
        if acoustic_raw >= 0.6:
            reasons.append("High acousticness, matching your preference")
    else:
        acoustic_raw = 1 - song["acousticness"]
        if acoustic_raw >= 0.6:
            reasons.append("Low acousticness, matching your preference")
    acoustic_fit = ACOUSTIC_WEIGHT * acoustic_raw

    # Apply optional scoring rules only when the listener sets a preference.
    favorite_decade = user_prefs.get("favorite_decade")
    decade_match = 0.0
    if favorite_decade is not None and song.get("release_decade") == favorite_decade:
        decade_match = DECADE_WEIGHT
        reasons.append(f"Matches your favorite era ({song['release_decade']})")

    prefers_popular = user_prefs.get("prefers_popular")
    popularity_fit = 0.0
    if prefers_popular is not None:
        popularity = song.get("popularity", 0)
        if prefers_popular:
            popularity_fit = POPULARITY_WEIGHT * (popularity / 100)
            if popularity >= 70:
                reasons.append("Popular track, matching your taste for well-known songs")
        else:
            popularity_fit = POPULARITY_WEIGHT * (1 - popularity / 100)
            if popularity <= 30:
                reasons.append("Under-the-radar track, matching your taste for hidden gems")

    user_keywords = {word.lower() for word in user_prefs.get("mood_keywords", [])}
    song_tags = {tag.lower() for tag in song.get("detailed_mood_tags", [])}
    mood_tag_fit = 0.0
    if user_keywords:
        matched_tags = user_keywords & song_tags
        mood_tag_fit = MOOD_TAG_WEIGHT * (len(matched_tags) / len(user_keywords))
        if matched_tags:
            reasons.append(f"Matches your mood keywords ({', '.join(sorted(matched_tags))})")

    favorite_language = user_prefs.get("favorite_language")
    language_match = 0.0
    if favorite_language is not None and song.get("language") == favorite_language:
        language_match = LANGUAGE_WEIGHT
        reasons.append(f"Matches your preferred language ({song['language']})")

    prefers_vocals = user_prefs.get("prefers_vocals")
    instrumental_fit = 0.0
    if prefers_vocals is not None:
        instrumentalness = song.get("instrumentalness", 0.0)
        instrumental_raw = 1 - instrumentalness if prefers_vocals else instrumentalness
        if instrumental_raw >= 0.8:
            if prefers_vocals:
                reasons.append("Strong vocals, matching your preference")
            else:
                reasons.append("Mostly instrumental, matching your preference")
        instrumental_fit = INSTRUMENTAL_WEIGHT * instrumental_raw

    score = (
        genre_match
        + mood_match
        + energy_closeness
        + acoustic_fit
        + decade_match
        + popularity_fit
        + mood_tag_fit
        + language_match
        + instrumental_fit
    )
    return score, reasons


def filter_eligible_songs(songs: List[Dict], allow_explicit: bool) -> List[Dict]:
    """Apply the explicit-content preference before scoring."""
    if allow_explicit:
        return songs
    return [song for song in songs if not song.get("explicit", False)]


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Return up to k eligible songs with scores and explanations."""
    # The CLI uses this same filter for catalog warnings and verification.
    candidates = filter_eligible_songs(
        songs, allow_explicit=user_prefs.get("allow_explicit", True)
    )

    scored = []
    for song in candidates:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    def ranking_key(entry: Tuple[Dict, float, str]) -> Tuple[float, float, int]:
        song, score, _ = entry
        energy_gap = abs(song["energy"] - user_prefs["target_energy"])

        # Python sorts ascending, so negate the score to put higher scores first.
        # Tied scores use the smallest energy gap, then the smallest song ID.
        return -score, energy_gap, song["id"]

    scored.sort(key=ranking_key)
    return scored[:k]