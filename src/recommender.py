import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

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
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user preferences, returning (score, reasons)."""
    reasons = []

    genre_match = 2.0 if song["genre"] == user_prefs["favorite_genre"] else 0.0
    if genre_match:
        reasons.append(f"Matches your favorite genre ({song['genre']})")

    mood_match = 1.5 if song["mood"] == user_prefs["favorite_mood"] else 0.0
    if mood_match:
        reasons.append(f"Matches your favorite mood ({song['mood']})")

    energy_closeness = 1.0 * max(0, 1 - abs(song["energy"] - user_prefs["target_energy"]))
    if energy_closeness >= 0.8:
        reasons.append("Energy closely matches your target")

    if user_prefs["likes_acoustic"]:
        acoustic_fit = 1.0 * song["acousticness"]
        if acoustic_fit >= 0.6:
            reasons.append("High acousticness, matching your preference")
    else:
        acoustic_fit = 1.0 * (1 - song["acousticness"])
        if acoustic_fit >= 0.6:
            reasons.append("Low acousticness, matching your preference")

    score = genre_match + mood_match + energy_closeness + acoustic_fit
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top k, ranked highest score first."""
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    scored.sort(key=lambda entry: entry[1], reverse=True)
    return scored[:k]
