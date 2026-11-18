import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field,asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    # Added attributes — all optional/defaulted so existing Song(...) calls still work.
    popularity: int = 0
    release_decade: str = ""
    detailed_mood_tags: List[str] = field(default_factory=list)
    explicit: bool = False
    language: str = ""
    instrumentalness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Added preferences — all optional, matching Song's added attributes.
    favorite_decade: Optional[str] = None
    prefers_popular: Optional[bool] = None
    mood_keywords: List[str] = field(default_factory=list)
    favorite_language: Optional[str] = None
    prefers_vocals: Optional[bool] = None
    allow_explicit: bool = True

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        songs_by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(
        asdict(user), [asdict(song) for song in self.songs], k=k
    )
        return [songs_by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv into a list of song dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
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
                "detailed_mood_tags": row["detailed_mood_tags"].split("|") if row["detailed_mood_tags"] else [],
                "explicit": row["explicit"].strip().lower() == "true",
                "language": row["language"],
                "instrumentalness": float(row["instrumentalness"]),
            })
    return songs

# Weight-shift experiment: genre halved (2.0 -> 1.0), energy doubled (1.0 -> 2.0).
GENRE_WEIGHT = 1.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 2.0
ACOUSTIC_WEIGHT = 1.0

# New-attribute weights. All five are optional on user_prefs — if the matching
# preference key is missing or None, that term contributes 0 and nothing crashes.
# Max possible score is now 5.5 (original four) + 3.5 (these five) = 9.0.
DECADE_WEIGHT = 1.0
POPULARITY_WEIGHT = 0.5
MOOD_TAG_WEIGHT = 1.0
LANGUAGE_WEIGHT = 0.5
INSTRUMENTAL_WEIGHT = 0.5

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user preferences, returning (score, reasons)."""
    reasons = []

    genre_match = GENRE_WEIGHT if song["genre"] == user_prefs["favorite_genre"] else 0.0
    if genre_match:
        reasons.append(f"Matches your favorite genre ({song['genre']})")

    mood_match = MOOD_WEIGHT if song["mood"] == user_prefs["favorite_mood"] else 0.0
    if mood_match:
        reasons.append(f"Matches your favorite mood ({song['mood']})")

    # Raw closeness (0-1) is kept separate from the weighted score so the
    # ">= 0.8" reason-text threshold still means "within 20% of target",
    # regardless of ENERGY_WEIGHT.
    energy_raw_closeness = max(0, 1 - abs(song["energy"] - user_prefs["target_energy"]))
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

    # --- New attributes ---

    favorite_decade = user_prefs.get("favorite_decade")
    decade_match = DECADE_WEIGHT if favorite_decade is not None and song.get("release_decade") == favorite_decade else 0.0
    if decade_match:
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

    user_keywords = {kw.lower() for kw in user_prefs.get("mood_keywords", [])}
    song_tags = {tag.lower() for tag in song.get("detailed_mood_tags", [])}
    if user_keywords:
        matched_tags = user_keywords & song_tags
        tag_overlap = len(matched_tags) / len(user_keywords)
        if matched_tags:
            reasons.append(f"Matches your mood keywords ({', '.join(sorted(matched_tags))})")
    else:
        tag_overlap = 0.0
    mood_tag_fit = MOOD_TAG_WEIGHT * tag_overlap

    favorite_language = user_prefs.get("favorite_language")
    language_match = LANGUAGE_WEIGHT if favorite_language is not None and song.get("language") == favorite_language else 0.0
    if language_match:
        reasons.append(f"Matches your preferred language ({song['language']})")

    prefers_vocals = user_prefs.get("prefers_vocals")
    instrumental_fit = 0.0
    if prefers_vocals is not None:
        instrumentalness = song.get("instrumentalness", 0.0)
        instrumental_raw = (1 - instrumentalness) if prefers_vocals else instrumentalness
        if instrumental_raw >= 0.8:
            reasons.append("Strong vocals, matching your preference" if prefers_vocals else "Mostly instrumental, matching your preference")
        instrumental_fit = INSTRUMENTAL_WEIGHT * instrumental_raw

    score = (
        genre_match + mood_match + energy_closeness + acoustic_fit
        + decade_match + popularity_fit + mood_tag_fit + language_match + instrumental_fit
    )
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top k, ranked highest score first."""
    # Explicit-content filter: on by default (allow_explicit=True) so callers
    # who never set this preference see the exact same candidate pool as before.
    allow_explicit = user_prefs.get("allow_explicit", True)
    candidates = songs if allow_explicit else [s for s in songs if not s.get("explicit", False)]

    scored = [
        (song, score, "; ".join(reasons))
        for song in candidates
        for score, reasons in [score_song(user_prefs, song)]
    ]
    scored.sort(key=lambda entry: entry[1], reverse=True)
    return scored[:k]
