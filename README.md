# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

- What features does each `Song` use in your system
  - Each `Song` carries nine attributes: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. My scoring rule only uses four of these — genre, mood, energy, and acousticness — because tempo, valence, and danceability move together with energy in this dataset, so including all of them would count the same "chill vs. intense" signal more than once.

- What information does your `UserProfile` store?
   - My `UserProfile` stores four preferences that line up one-to-one with those four features: `favorite_genre`, `favorite_mood`, `target_energy`, and `likes_acoustic`.

- How does your `Recommender` compute a score for each song? (finalized algorithm recipe)
  - My `Recommendar` scores each song against a user with four weighted rules that add up to a single number, with a maximum possible score of 5.5 (2.0 + 1.5 + 1.0 + 1.0):

    ```
    genre_match       = 2.0 if song.genre == user.favorite_genre else 0.0
    mood_match        = 1.5 if song.mood  == user.favorite_mood  else 0.0
    energy_closeness  = 1.0 * max(0, 1 - abs(song.energy - user.target_energy))
    acoustic_fit      = 1.0 * song.acousticness        if user.likes_acoustic
                      = 1.0 * (1 - song.acousticness)  if not user.likes_acoustic

    score = genre_match + mood_match + energy_closeness + acoustic_fit
    ```

    - **Genre match (+2.0)** — exact match only, no partial credit for related genres (e.g. "indie pop" does not match "pop").
    - **Mood match (+1.5)** — exact match only.
    - **Energy closeness (0 to +1.0)** — linear decay from the user's target energy. This rewards songs whose energy is close to what the user wants in either direction, rather than just favoring higher or lower energy outright.
    - **Acoustic fit (0 to +1.0)** — rewards acousticness in whichever direction the user actually prefers.

    Genre outweighs mood (2.0 vs 1.5) since genre is a firmer taste signal, but neither is decisive alone — a genre hit with everything else missed (2.0) can still lose to a genre miss with mood + energy + acoustic all hit (up to 3.5). Categorical weight (3.5 max) outweighs numeric weight (2.0 max) overall, since genre/mood are the user's explicit stated preferences and energy/acoustic are secondary refinements.

  **Worked example** — `user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)`

  | Song | Genre | Mood | Energy | Acoustic | Score |
  |---|---|---|---|---|---|
  | Sunrise City | pop ✓ (+2.0) | happy ✓ (+1.5) | 0.82 (+0.98) | 0.18 (+0.82) | **5.30** |
  | Gym Hero | pop ✓ (+2.0) | intense (+0) | 0.93 (+0.87) | 0.05 (+0.95) | **3.82** |
  | Rooftop Lights | indie pop (+0) | happy ✓ (+1.5) | 0.76 (+0.96) | 0.35 (+0.65) | **3.11** |

  Ranking matches intuition: the exact pop/happy/high-energy/non-acoustic track wins clearly.

- How do you choose which songs to recommend
  - To choose which songs to recommend, I score every song in the catalog, sort the results from highest to lowest total score, and return the top `k`. On a tie, I break it by whichever song has the closer energy match, since that's the most fine-grained signal left once genre, mood, and acoustic fit are equal.

  I kept scoring (one song in, one number out) and ranking (the whole list in, an ordered top-k out) as two separate steps, matching `score_song()` and `recommend_songs()` in `recommender.py`: scoring never needs to know about any other song, while sorting, tie-breaking, and the `k` cutoff only make sense once every song's score is known.

- Data flow, end to end

  ```
  INPUT
    user_prefs: { favorite_genre, favorite_mood, target_energy, likes_acoustic }
                  │
                  ▼
    songs: List[Dict]  ◄── load_songs(csv_path)   [reads data/songs.csv]
                  │
                  ▼
  ┌─────────────────────────────────────────────────────────┐
  │ PROCESS — recommend_songs(user_prefs, songs, k)            │
  │                                                             │
  │  for song in songs:                                        │
  │      score, reasons = score_song(user_prefs, song)         │
  │          ├─ genre match        → +2.0 / 0                  │
  │          ├─ mood match         → +1.5 / 0                  │
  │          ├─ energy closeness   → +0 to 1.0 (linear decay)  │
  │          └─ acoustic fit       → +0 to 1.0 (direction-aware)│
  │      scored.append((song, score, reasons))                 │
  │                                                             │
  │  sort scored by score, descending (tie-break: closer energy)│
  │  take top k                                                │
  └─────────────────────────────────────────────────────────┘
                  │
                  ▼
  OUTPUT
    List[(song, score, explanation)]
    top-k, ranked highest → lowest, with `reasons` joined into
    a plain-language explanation for each pick
  ```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

User profile: favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False

```
Top Recommendations
========================================

1. Sunrise City (5.30 pts)
   - Matches your favorite genre (pop)
   - Matches your favorite mood (happy)
   - Energy closely matches your target
   - Low acousticness, matching your preference

2. Gym Hero (3.82 pts)
   - Matches your favorite genre (pop)
   - Energy closely matches your target
   - Low acousticness, matching your preference

3. Rooftop Lights (3.11 pts)
   - Matches your favorite mood (happy)
   - Energy closely matches your target
   - Low acousticness, matching your preference

4. Fractal Bloom (1.85 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

5. Iron Will (1.81 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

**Potential biases to expect from the scoring rules above:**

- **Genre/mood lock-in.** Because genre and mood are exact-string, binary matches worth the two highest weights (2.0 and 1.5), a user's stated preference dominates the ranking — songs in a slightly different but related genre (e.g. "indie pop" vs "pop") get zero credit even if they'd otherwise be a great fit. This can create a filter bubble: the system will keep surfacing the same genre/mood pair and rarely surface adjacent styles a user might also enjoy.
- **Catalog imbalance.** If the CSV has far more songs in some genres/moods than others, users with a popular favorite genre get a large pool to rank from, while users with an underrepresented genre get thin, lower-quality top-k results — the scoring rule itself is neutral, but it inherits whatever imbalance exists in `data/songs.csv`.
- **Acoustic/energy preferences are binary and self-reported.** `likes_acoustic` and `target_energy` assume the user's stated preference is fixed and always correct; the system never adapts based on observed behavior, so a one-time or inaccurate preference will systematically mis-score every recommendation for that user.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



## User Profile : 

Taste profile : favorite genre 