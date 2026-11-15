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

I ran a batch of adversarial / edge-case user profiles through `recommend_songs()` to see whether the scoring logic could be tricked into producing unexpected rankings. All runs used `data/songs.csv` and `k=5`.

### 1. Case / whitespace mismatch on genre & mood

`score_song()` compares `genre`/`mood` with plain `==`, so anything that isn't a byte-for-byte match (capitalization, stray whitespace) silently scores as a miss — no error, no warning.

**1a. `favorite_genre="Pop"`, `favorite_mood="Happy"`** (CSV stores them lowercase)

```
User profile: {'favorite_genre': 'Pop', 'favorite_mood': 'Happy', 'target_energy': 0.8, 'likes_acoustic': False}

Top Recommendations
========================================

1. Fractal Bloom (1.85 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

2. Gym Hero (1.82 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

3. Iron Will (1.81 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

4. Sunrise City (1.80 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

5. Carnival Nights (1.80 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference
```

Sunrise City — the song the worked example above says should score **5.30** and rank #1 — drops to #4 at **1.80** because `"Pop" != "pop"` and `"Happy" != "happy"`. Genre and mood contribute nothing at all for this profile.

**1b. `favorite_genre="pop "`** (trailing space)

```
User profile: {'favorite_genre': 'pop ', 'favorite_mood': 'chill', 'target_energy': 0.5, 'likes_acoustic': True}

Top Recommendations
========================================

1. Library Rain (3.21 pts)
   - Matches your favorite mood (chill)
   - Energy closely matches your target
   - High acousticness, matching your preference

2. Spacewalk Thoughts (3.20 pts)
   - Matches your favorite mood (chill)
   - High acousticness, matching your preference

3. Midnight Coding (3.13 pts)
   - Matches your favorite mood (chill)
   - Energy closely matches your target
   - High acousticness, matching your preference

4. Coffee Shop Stories (1.76 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference

5. Starlit Lullaby (1.70 pts)
   - High acousticness, matching your preference
```

No pop song shows up anywhere in the top 5 — a single trailing space erased the entire genre preference.

### 2. `target_energy` outside the documented 0–1 range

**2a. `target_energy=5.0`**

```
User profile: {'favorite_genre': 'lofi', 'favorite_mood': 'chill', 'target_energy': 5.0, 'likes_acoustic': True}

Top Recommendations
========================================

1. Library Rain (4.36 pts)
   - Matches your favorite genre (lofi)
   - Matches your favorite mood (chill)
   - High acousticness, matching your preference

2. Midnight Coding (4.21 pts)
   - Matches your favorite genre (lofi)
   - Matches your favorite mood (chill)
   - High acousticness, matching your preference

3. Focus Flow (2.78 pts)
   - Matches your favorite genre (lofi)
   - High acousticness, matching your preference

4. Spacewalk Thoughts (2.42 pts)
   - Matches your favorite mood (chill)
   - High acousticness, matching your preference

5. Starlit Lullaby (0.95 pts)
   - High acousticness, matching your preference
```

**2b. `target_energy=-2.0`**

```
User profile: {'favorite_genre': 'rock', 'favorite_mood': 'intense', 'target_energy': -2.0, 'likes_acoustic': False}

Top Recommendations
========================================

1. Storm Runner (4.40 pts)
   - Matches your favorite genre (rock)
   - Matches your favorite mood (intense)
   - Low acousticness, matching your preference

2. Gym Hero (2.45 pts)
   - Matches your favorite mood (intense)
   - Low acousticness, matching your preference

3. Iron Will (0.97 pts)
   - Low acousticness, matching your preference

4. Fractal Bloom (0.92 pts)
   - Low acousticness, matching your preference

5. Sunrise City (0.82 pts)
   - Low acousticness, matching your preference
```

In both cases `energy_closeness` clamps to `0` for every song (`max(0, 1 - abs(...))`), since no song's energy is within 1.0 of a target of 5.0 or -2.0. The ranking degrades gracefully to genre + mood + acoustic only, but silently — nothing tells the user their stated preference is out of bounds and being ignored.

### 3. Genre/mood that doesn't exist anywhere in the catalog

```
User profile: {'favorite_genre': 'opera', 'favorite_mood': 'euphoric', 'target_energy': 0.5, 'likes_acoustic': False}

Top Recommendations
========================================

1. Velvet Promises (1.60 pts)
   - Energy closely matches your target
   - Low acousticness, matching your preference

2. Fractal Bloom (1.55 pts)
   - Low acousticness, matching your preference

3. Night Drive Loop (1.53 pts)
   - Low acousticness, matching your preference

4. Gym Hero (1.52 pts)
   - Low acousticness, matching your preference

5. Iron Will (1.51 pts)
   - Low acousticness, matching your preference
```

`genre_match` and `mood_match` are `0.0` for every song, so the "recommendations" are driven entirely by energy + acoustic fit — effectively ignoring the two preferences the user stated explicitly. The system never flags that it couldn't find any genre/mood match.

### 4. Boundary value on the acousticness reason-text threshold

```
User profile: {'favorite_genre': 'jazz', 'favorite_mood': 'relaxed', 'target_energy': 0.37, 'likes_acoustic': True}

Top Recommendations
========================================

1. Coffee Shop Stories (5.39 pts)
   - Matches your favorite genre (jazz)
   - Matches your favorite mood (relaxed)
   - Energy closely matches your target
   - High acousticness, matching your preference

2. Library Rain (1.84 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference

3. Spacewalk Thoughts (1.83 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference

4. Starlit Lullaby (1.83 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference

5. Quiet Pastures (1.81 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference
```

This one scored as expected — no surprises, just confirms the `>= 0.6` reason-text threshold reads correctly near the boundary.

### 5. Attempt to force a score tie

```
User profile: {'favorite_genre': 'ambient', 'favorite_mood': 'chill', 'target_energy': 0.28, 'likes_acoustic': True}

Top Recommendations
========================================

1. Spacewalk Thoughts (5.42 pts)
   - Matches your favorite genre (ambient)
   - Matches your favorite mood (chill)
   - Energy closely matches your target
   - High acousticness, matching your preference

2. Library Rain (3.29 pts)
   - Matches your favorite mood (chill)
   - Energy closely matches your target
   - High acousticness, matching your preference

3. Midnight Coding (3.07 pts)
   - Matches your favorite mood (chill)
   - Energy closely matches your target
   - High acousticness, matching your preference

4. Starlit Lullaby (1.92 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference

5. Quiet Pastures (1.86 pts)
   - Energy closely matches your target
   - High acousticness, matching your preference
```

This particular profile didn't land an exact tie in the top 5 — two songs outside the top 5 (Velvet Promises / Golden Hour Drive) rounded to the same displayed score (1.18) but differed at full float precision (1.18 vs 1.1800000000000002), so they weren't actually tied. Digging further with a brute-force search did turn up a genuine exact tie elsewhere in the catalog (`favorite_genre="ambient"`, `favorite_mood="angry"`, `target_energy=0.0`, `likes_acoustic=True` ties Golden Hour Drive and Velvet Promises at exactly 0.9). That confirmed a real bug: `recommend_songs()` only sorts by `(song, score, reason)` on `score` — it never breaks ties by energy closeness the way the README (line 59) claims it does. Tied songs just keep whatever order they happened to have in the original CSV.

**Takeaway:** the scoring formula itself behaves as documented, but the surrounding system has no input validation (case/whitespace sensitivity, no range-checking on `target_energy`) and the documented tie-breaking rule isn't actually implemented in code.

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