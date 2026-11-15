# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeCheck 1.0**

It checks how well a song's "vibe" (genre, mood, energy, acoustic feel) matches what you asked for.

---

## 2. Goal / Task, Intended Use, and Non-Intended Use

**Goal / Task**

- VibeCheck looks at a small catalog of songs.
- It picks the top 5 songs that best match one listener's stated taste.
- "Taste" means four things: favorite genre, favorite mood, target energy level, and whether the listener likes acoustic sound.
- It does **not** predict what you'll actually enjoy. It only measures how closely a song's tags match the words and numbers you typed in.

**Intended Use**

- This is a classroom project, not a real product.
- It's meant to show how a simple scoring rule can turn raw data into ranked recommendations.
- It's good for exploring how recommender systems work and where they go wrong.

**Non-Intended Use**

- Don't use this for real listeners or a real app. It hasn't been built or tested for that.
- Don't trust it to judge anyone's "correct" taste in music. It only checks exact word matches, not actual quality or fit.
- Don't plug in a bigger real-world catalog without fixing the bugs we found (see Section 5). They get worse at scale.

---

## 3. Algorithm Summary

Think of it like a judge scoring a contest. Every song gets compared to the listener's taste, one at a time. The highest scores win a spot in the top 5.

Each song earns points in four ways:

- **Genre match** — biggest point value. Exact match only. "Indie pop" does not count as "pop."
- **Mood match** — second-biggest point value. Exact match only.
- **Energy match** — a sliding scale, not yes/no. The closer the song's energy is to the listener's target, the more points it earns.
- **Acoustic match** — also a sliding scale. More acoustic songs score higher for listeners who like acoustic sound. Less acoustic songs score higher for listeners who don't.

All four point values get added into one score. Songs get sorted from highest score to lowest. The top 5 get recommended.

Genre and mood count for the most, because they're what the listener directly told the system they want. Energy and acoustic feel are smaller boosts that fine-tune the order.

Each recommendation also comes with plain-text reasons, like "matches your favorite genre" or "energy closely matches your target," so the listener can see why a song was picked.

---

## 4. Data Used

- The catalog has **18 songs** total. That's small — more like a demo playlist than a real streaming library.
- Each song has 10 fields: id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
- Only **4 of those 10 fields** actually get used in scoring: genre, mood, energy, and acousticness. Tempo, valence, and danceability are loaded but never scored, because they move together with energy in this dataset and would just double-count the same signal.
- There are **15 different genres** across 18 songs. Most genres show up only once (metal, rock, folk, classical, etc). Only "pop" and "lofi" show up more than once.
- There are **14 different moods**, and most of those show up only once too.
- Energy only ranges from 0.25 to 0.96 in this catalog — nobody asked for pure "0" or pure "1" energy, so that part of the scale is never fully reachable.
- We didn't add or remove any songs. This is the starter dataset as given.
- Missing from the data: no lyrics, no language or vocal style, no actual listener behavior (nobody's play history or skip rate), and no way to tell if two genres are "close" to each other.

---

## 5. Observed Behavior / Biases

**One clear bias we found:** energy and acousticness move in lockstep in this catalog. We measured it — they're correlated at **r = -0.976**, almost a perfect inverse relationship. Every high-energy song is low-acoustic, and every low-energy song is high-acoustic. No song is both intense *and* acoustic-sounding.

- This means a listener who wants **high energy + acoustic sound** (an unusual combo) can never get a great match. No song in the catalog can satisfy both halves of that preference at once.
- The scoring treats energy and acousticness as two separate signals, but in this dataset they're really measuring the same "mellow vs. intense" idea twice.
- The system can't tell when this is happening. It just quietly gives that listener lower scores across the board, with no warning.
- This isn't a bug in the math. The formula is doing exactly what it was told to do. The bias comes from the shape of the catalog, not the scoring rule itself.

We also found a second issue while testing: the genre and mood matching is **case- and whitespace-sensitive**. Typing `"Pop"` instead of `"pop"`, or adding a stray space, silently zeroes out the two most important score ingredients with no warning or error. See Section 6 for the full test results.

---

## 6. Evaluation Process

We tested **8 user profiles** total: 1 normal "control" profile, plus 7 edge cases designed to try to break the scoring logic.

| # | Profile | What we were checking |
|---|---|---|
| 0 | Happy Pop fan, typed correctly | The "normal" baseline case |
| 1a | Same fan, but typed `"Pop"` / `"Happy"` (capitals) | Does case matter? |
| 1b | Chill/acoustic fan who typed `"pop "` (trailing space) | Does whitespace matter? |
| 2a | Lo-fi/chill fan with `target_energy = 5.0` | What happens outside the 0–1 scale? |
| 2b | Rock/intense fan with `target_energy = -2.0` | Same, but negative |
| 3 | Fan of a genre/mood not in the catalog at all (`opera` / `euphoric`) | What if we don't carry that taste? |
| 4 | Chill jazz fan who likes acoustic sound | A clean, correctly-typed comparison case |
| 5 | Ambient/chill fan | Can we force two songs to tie exactly? |

**Comparisons we made, in short:**

- **Profile 0 vs. 1a:** same listener, just typed with capital letters. Result: the system treats it as a totally different (and much worse) match. That's a bug, not something that makes sense.
- **Profile 0 vs. Profile 4:** two real, different listeners (upbeat pop fan vs. mellow jazz fan). Result: two clearly different, sensible playlists — bright and energetic vs. soft and acoustic. This is the system working the way it should.
- **Profile 2a vs. 2b:** both typed an impossible energy number. Result: the system ignores the broken energy input and quietly falls back to genre and mood. It doesn't crash, but it never tells the listener their energy pick was ignored.
- **Profile 3 vs. Profile 0:** one taste exists in the catalog, one doesn't. Result: the "opera" fan gets a much weaker, lower-confidence top pick — not because their taste is bad, but because we don't stock that genre.
- **Profile 1b vs. Profile 4:** both are going for a "mellow and acoustic" vibe. Result: similar-sounding songs come back for both, but Profile 4's exact genre match gives it a much more confident #1 pick, while Profile 1b's broken genre field leaves a thin, close race at the top.

**A question we dug into:** why does "Gym Hero" (a pop song, but tagged *intense*, not *happy*) keep showing up near the top for a "Happy Pop" fan? Answer: the system doesn't need a perfect match. It adds up partial credit. Gym Hero nails genre, energy, and acoustic feel — it only misses on mood. Three out of four strong matches is still enough to beat songs that don't nail anything.

**What surprised us most:** the case/whitespace bug. The math is correct, but a single capital letter or stray space can silently erase someone's entire stated taste, with zero warning. We also found that `recommend_songs()` never actually breaks ties by energy closeness, even though the README said it would — ties just fall back to whatever order the songs happen to sit in the CSV file.

*(Full test output and exact profile dictionaries are available in the project's README under "Experiments You Tried.")*

---

## 7. Ideas for Improvement

1. **Normalize genre and mood text before comparing it** — lowercase and trim whitespace on both sides of the match, so `"Pop"`, `"pop "`, and `"pop"` are all treated the same.
2. **Actually implement the tie-break rule** — right now ties just fall back to CSV order. Sorting by energy closeness as a tiebreaker (like the docs already claim it does) would make results more predictable.
3. **Warn the user when a preference can't be matched** — if `target_energy` is out of range, or the favorite genre/mood doesn't exist in the catalog, tell the listener instead of silently falling back to a weaker recommendation.

---

## 8. Strengths  

- **It nails the "easy" cases.** When a listener's favorite genre and mood actually exist in the catalog and get typed correctly, the top pick is usually a clear, obvious winner. The Happy Pop fan test scored 5.30 out of a possible 5.5 — about as close to a perfect match as this system can produce.
- **It tells different tastes apart.** The pop/energetic fan and the jazz/acoustic fan got two completely different, sensible playlists — bright and upbeat vs. soft and mellow. That's exactly what should happen for two different listeners.
- **Partial credit feels human.** A song doesn't need to be a perfect match to rank well. "Gym Hero" still shows up near the top for a Happy Pop fan because it nails genre, energy, and acoustic feel, even though its mood tag is "intense" instead of "happy." That mirrors how a real person might think — "close enough, I'd probably still like this."
- **It fails safe, not loud.** Bad input (an energy value way outside 0–1, or a genre we don't stock) never crashes the system. It just falls back to whatever signals still work.
- **The explanations build trust.** Every recommendation comes with plain-text reasons ("matches your favorite genre," "energy closely matches your target"), so it never feels like a black box handing out a mystery number.

---

## 9. Personal Reflection  

Building this made me realize a "recommender" can be a lot simpler than it sounds — underneath, it's just addition and sorting. There's no learning, no intelligence, just a scoring rule applied to every row and a ranked list at the end. That demystified the idea for me a bit.

The most surprising thing was how fragile that simple scoring turned out to be. A single capital letter or stray space in the genre field was enough to silently wipe out someone's entire stated taste, with no error and no warning. I didn't expect a tiny typo to matter that much. Just as surprising was finding that energy and acousticness were almost perfectly correlated in this dataset (r = -0.976) — two features that were supposed to measure different things were secretly measuring the same thing twice.

This changed how I think about real music apps. If a tiny 18-song demo catalog can hide a bias like that, I have to assume real streaming services have far messier versions of the same problem — just buried under more data and more complexity, so it's harder to notice. It made me a lot more curious about what's actually happening behind a "recommended for you" playlist, instead of just trusting that it's smart.
