import pytest
from src.recommender import Recommender, Song, UserProfile
from src.main import CATALOG_PATH, main
from src.recommender import load_songs, recommend_songs
from src.reliability import verify_recommendations


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




def test_ranking_is_consistent_across_case_and_whitespace():
    songs = load_songs(str(CATALOG_PATH))
    preferences = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }

    normal = recommend_songs(preferences, songs, k=3)
    mixed_case = recommend_songs(
        {**preferences, "favorite_genre": " Pop ", "favorite_mood": " HAPPY "},
        songs,
        k=3,
    )

    # Compare the ordering, scores, and explanations across equivalent inputs.
    assert mixed_case == normal
    assert len(normal) == 3
    assert normal[0][0]["title"] == "Sunrise City"


@pytest.mark.parametrize("energy", ["1.5", "-0.2", "NaN"])
def test_cli_rejects_invalid_energy(energy, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "--energy", energy])

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert "--energy must be a finite number between 0 and 1" in captured.err
    assert "Top Recommendations" not in captured.out


def test_cli_excludes_explicit_track_and_warns(monkeypatch, capsys):
    args = [
        "main.py",
        "--genre", "metal",
        "--mood", "angry",
        "--energy", "0.96",
        "--top-k", "3",
    ]

    # Confirm that Iron Will ranks first when explicit tracks are allowed.
    monkeypatch.setattr("sys.argv", args)
    assert main() == 0
    assert "1. Iron Will" in capsys.readouterr().out

    # Repeat the request with explicit tracks excluded.
    monkeypatch.setattr("sys.argv", [*args, "--exclude-explicit"])
    assert main() == 0
    output = capsys.readouterr().out

    assert "Iron Will" not in output
    assert "No eligible songs match the genre 'metal'" in output
    assert "No eligible songs match the mood 'angry'" in output
    assert "Showing partial matches" in output
    assert "Top Recommendations" in output


def test_ranking_breaks_score_ties_by_energy_gap_then_id():
    preferences = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.5,
        "likes_acoustic": True,
    }

    # All three songs score 4.5. Acousticness offsets the energy difference.
    common = {"genre": "pop", "mood": "happy"}
    songs = [
        {**common, "id": 1, "energy": 0.25, "acousticness": 0.5},
        {**common, "id": 3, "energy": 0.5, "acousticness": 0.0},
        {**common, "id": 2, "energy": 0.5, "acousticness": 0.0},
    ]

    ranked = recommend_songs(preferences, songs, k=3)

    assert [score for _, score, _ in ranked] == [4.5, 4.5, 4.5]
    assert [song["id"] for song, _, _ in ranked] == [2, 3, 1]


@pytest.mark.parametrize(
    ("second_id", "expected_error"),
    [(1, "appears more than once"), (99, "outside the eligible catalog")],
)
def test_verifier_rejects_invalid_song_ids(second_id, expected_error):
    eligible_songs = [{"id": 1}, {"id": 2}]
    recommendations = [
        ({"id": 1}, 4.0, "First match"),
        ({"id": second_id}, 3.0, "Second match"),
    ]

    with pytest.raises(ValueError, match=expected_error):
        verify_recommendations(recommendations, eligible_songs, top_k=2)