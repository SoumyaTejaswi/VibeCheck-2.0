"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_ac oustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop Recommendations")
    print("=" * 40)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} ({score:.2f} pts)")
        reasons = explanation.split("; ") if explanation else []
        if reasons:
            for reason in reasons:
                print(f"   - {reason}")
        else:
            print("   - No strong matches with your preferences")
    print()


if __name__ == "__main__":
    main()
