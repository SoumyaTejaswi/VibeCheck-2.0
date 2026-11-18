# VibeCheck 2.0 — Applied Music Recommender

VibeCheck recommends songs from a local catalog based on a listener’s genre, mood, energy, and acoustic preferences. It ranks tracks by match score and explains which preferences contributed to each recommendation. It also checks the results before displaying them and warns when the eligible catalog cannot satisfy a requested genre or mood.

## Original Module 3 project

This project extends the [Module 3 Music Recommender Simulation](https://github.com/SoumyaTejaswi/ai110-module3show-musicrecommendersimulation-starter). The original project used a weighted scoring rule to rank songs against a sample listener profile and explain each match. VibeCheck 2.0 adds a configurable command-line interface, input validation, catalog coverage warnings, deterministic tie-breaking, and automated reliability tests.

## Architecture

The [Mermaid architecture source](diagrams/architecture.mmd) shows how listener preferences move through the system.

1. **Parse and validate input.** `src/main.py` reads the command-line arguments. `src/reliability.py` normalizes the genre and mood and rejects invalid values before ranking starts.
2. **Load and filter songs.** The app reads `data/songs.csv`. If the listener requests explicit-track exclusion, the app removes those tracks before checking catalog coverage or scoring.
3. **Score and rank.** `src/recommender.py` calculates match scores and generates explanations. When scores tie, the smaller energy gap ranks first, followed by the lower song ID.
4. **Verify and display.** Before printing, the app checks the result count, catalog eligibility, unique song IDs, finite scores, and descending score order. The listener sees the ranked songs, explanations, and any catalog warnings.

The automated tests exercise both the ranking functions and the command-line behavior.

## Setup and usage

Use Python 3.9 or later. From the repository root, create a virtual environment and install the dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the default profile or view the available options.

```bash
python -m src.main
python -m src.main --help
```

The default profile requests happy pop tracks, a target energy of `0.8`, and a preference for lower acousticness. Use `--acoustic` to prefer more acoustic tracks, `--exclude-explicit` to remove explicit tracks, and `--top-k` to set the number of results.

## Design decisions

- **Explainable scoring.** The four CLI preferences contribute up to 5.5 points. Genre contributes up to `1.0`, mood up to `1.5`, energy closeness up to `2.0`, and acoustic fit up to `1.0`. Each score describes how closely a track’s metadata fits the request.
- **Predictable matching.** Genre and mood matching ignore capitalization and surrounding spaces. Labels still match exactly after normalization, so `pop` and `indie pop` remain distinct genres.
- **Partial matches with a warning.** A valid preference can be missing from the eligible catalog. In that case, the app explains the coverage gap and recommends tracks using the other preferences. Invalid input, such as an out-of-range energy value, stops the request.
- **Reproducible ranking.** The catalog and scoring rules produce repeatable results. The small catalog limits the range of preferences the system can satisfy.

## Reproducible execution evidence

### Example 1 — Rank songs for a happy pop profile

```text
$ python -m src.main --genre pop --mood happy --energy 0.8 --top-k 3

Top Recommendations
========================================

1. Sunrise City (match score: 5.28)
   - Matches your favorite genre (pop)
   - Matches your favorite mood (happy)
   - Energy closely matches your target
   - Low acousticness, matching your preference

2. Rooftop Lights (match score: 4.07)
   - Matches your favorite mood (happy)
   - Energy closely matches your target
   - Low acousticness, matching your preference

3. Gym Hero (match score: 3.69)
   - Matches your favorite genre (pop)
   - Energy closely matches your target
   - Low acousticness, matching your preference
```

`Sunrise City` ranked first and matched all four preferences. The other tracks show how the scorer ranks partial matches.

### Example 2 — Exclude explicit tracks and show catalog warnings

```text
$ python -m src.main --genre metal --mood angry --energy 0.96 --exclude-explicit --top-k 3
Warning: No eligible songs match the genre 'metal'.
Warning: No eligible songs match the mood 'angry'.
Warning: Showing partial matches based on your other preferences.

Top Recommendations
========================================

1. Gym Hero (match score: 2.89)
   - Energy closely matches your target
   - Low acousticness, matching your preference

2. Storm Runner (match score: 2.80)
   - Energy closely matches your target
   - Low acousticness, matching your preference

3. Fractal Bloom (match score: 2.74)
   - Energy closely matches your target
   - Low acousticness, matching your preference
```

The explicit-content filter excluded `Iron Will`. The app reported that no eligible tracks matched the requested genre or mood and returned three tracks based on energy and acoustic fit.

### Example 3 — Reject an out-of-range energy value

```text
$ python -m src.main --energy 1.5
usage: main.py [-h] [--genre GENRE] [--mood MOOD] [--energy ENERGY] [--acoustic | --no-acoustic]
               [--exclude-explicit] [--top-k TOP_K]
main.py: error: --energy must be a finite number between 0 and 1.

$ echo $?
2
```

The app reported the valid range and exited with status `2` before printing any recommendations.

## Reliability testing

```text
$ python -m pytest tests/test_recommender.py -q
.......... [100%]
10 passed in 0.02s
```

| Check | Expected behavior | Observed behavior | Result |
| --- | --- | --- | --- |
| Happy pop profile | The best match ranks first with an explanation. | `Sunrise City` ranked first at `5.28` with four matching reasons. | Pass |
| Capitalization and whitespace | Equivalent labels produce identical rankings, scores, and explanations. | `pop` and `happy` produced the same results as ` Pop ` and ` HAPPY `. | Pass |
| Explicit-content exclusion | Explicit tracks are excluded and missing preferences trigger warnings. | `Iron Will` was excluded. Metal and angry coverage warnings appeared alongside partial matches. | Pass |
| Invalid energy | Out-of-range values and `NaN` are rejected before the playlist is shown. | All three automated cases passed. The manual `1.5` run exited with status `2`. | Pass |
| Tied scores | The smallest energy gap ranks first, followed by the lowest song ID. | Three equal-score test tracks returned in the expected order, `[2, 3, 1]`. | Pass |
| Invalid recommendation IDs | The verifier rejects duplicates and IDs outside the eligible catalog. | Both invalid-ID cases raised the expected errors. | Pass |

## Reflection

This project showed me how small input differences can change recommendations if the system compares raw text. I used an automated test to confirm that capitalization and surrounding spaces now produce identical results. The explicit-track example also showed why a recommendation system should tell listeners when its catalog can only meet part of their request.

The tests measure the recommender’s behavior on known cases. Listener satisfaction would require feedback from people using the recommendations. See the [model card](model_card.md) for limitations, potential misuse, and reflection on AI collaboration.
