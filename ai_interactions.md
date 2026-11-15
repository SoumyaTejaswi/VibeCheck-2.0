# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Claude Code to extend the song catalog with new, more complex attributes (not just the original genre/mood/energy/acoustic fields), and then to wire those new attributes into the actual scoring logic in `recommender.py` — not just leave them sitting unused in the CSV. This was a multi-step, multi-file change: new data columns, updated data loading, updated scoring math, and a backward-compatibility check, all done autonomously in one pass.

**Prompts used:**

- "Can you introduce 5 or more complex attributes to our dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., 'nostalgic,' 'aggressive,' 'euphoric')."
- "Okay now Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes."

**What did the agent generate or change?**

- `data/songs.csv`: added 6 new columns to all 18 existing songs — `popularity` (0–100), `release_decade`, `detailed_mood_tags` (pipe-separated, e.g. `uplifting|carefree|sunny`), `explicit` (bool), `language`, and `instrumentalness` (0–1). Values were hand-written to stay consistent with each song's existing genre/mood/energy (e.g., lo-fi/ambient tracks got high `instrumentalness`, the one aggressive metal track got `explicit=True`).
- `src/recommender.py`:
  - Extended the `Song` and `UserProfile` dataclasses with matching optional fields, all defaulted so existing code that constructs them stays valid.
  - Updated `load_songs()` to parse and type-convert all 6 new columns.
  - Added 5 new weighted scoring terms to `score_song()`: decade match, popularity fit (direction-aware), mood-keyword overlap (partial credit), language match, and instrumental fit (direction-aware). Max possible score rose from 5.5 to 9.0.
  - Updated `recommend_songs()` to hard-filter out `explicit=True` songs when a user sets `allow_explicit=False`, instead of just scoring them lower.
  - Every new preference is read with `.get()` and defaults to "no effect," so a profile that doesn't use the new fields behaves exactly as before.

**What did you verify or fix manually?**

- Re-ran the existing test suite (`PYTHONPATH=. pytest`) after the dataclass changes — both tests still passed, confirming the new optional fields didn't break anything.
- Ran an old-style profile (no new keys) through `recommend_songs()` and confirmed the scores and ranking were unchanged from before the update — true backward compatibility, not just "no crash."
- Ran a new-style profile using all 5 new preferences at once and manually checked the printed "reasons" list and point total added up to the expected 9.0-point max.
- Ran an `allow_explicit=False` profile and confirmed the one explicit song ("Iron Will") was excluded from the results entirely, not just down-ranked.
- Flagged, but did not act on without asking, that `algorithmRecipe.md`, `README.md`, and `model_card.md` still describe the old 4-feature/5.5-point recipe and would drift out of sync with the code unless updated in a follow-up.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
