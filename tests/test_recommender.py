from src.recommender import Recommender, Song, UserProfile


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    results = rec.recommend(user, k=2)

    assert [song.id for song in results] == [1, 2]


def test_explain_recommendation_mentions_matching_genre_and_mood():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    pop_song = next(song for song in rec.songs if song.id == 1)

    explanation = rec.explain_recommendation(user, pop_song)

    assert "Matches your favorite genre (pop)" in explanation
    assert "Matches your favorite mood (happy)" in explanation