# Scoring Recipe

Score = Genre Match + Mood Match + Energy Closeness + Acoustic Fit
Max possible score = 5.5 (2.0 + 1.5 + 1.0 + 1.0)

## Rules

**Genre Match (weight 2.0)** — exact match only, no partial credit for related genres.
```
genre_match = 2.0 if song.genre == user.favorite_genre else 0.0
```

**Mood Match (weight 1.5)** — exact match only.
```
mood_match = 1.5 if song.mood == user.favorite_mood else 0.0
```

**Energy Closeness (weight 1.0)** — linear decay based on distance from the user's target energy (both already on a 0-1 scale, so no normalization needed).
```
energy_closeness = 1.0 * max(0, 1 - abs(song.energy - user.target_energy))
```

**Acoustic Fit (weight 1.0)** — rewards acousticness in the direction the user prefers.
```
acoustic_fit = 1.0 * song.acousticness        if user.likes_acoustic
acoustic_fit = 1.0 * (1 - song.acousticness)  if not user.likes_acoustic
```

Genre outweighs mood (2.0 vs 1.5) since genre is a firmer taste signal, but one still isn't decisive on its own — a genre hit with a mood/energy/acoustic miss (2.0) can still be beaten by a genre miss with everything else hit (1.5 + up to 2.0). Categorical max (3.5) outweighs numeric max (2.0) overall, since genre/mood are the user's explicit stated preferences and energy/acoustic are secondary refinements.

## Worked example

`user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)`

| Song | Genre | Mood | Energy | Acoustic | Score |
|---|---|---|---|---|---|
| Sunrise City | pop ✓ (+2.0) | happy ✓ (+1.5) | 0.82 (+0.98) | 0.18 (+0.82) | **5.30** |
| Gym Hero | pop ✓ (+2.0) | intense (+0) | 0.93 (+0.87) | 0.05 (+0.95) | **3.82** |
| Rooftop Lights | indie pop (+0) | happy ✓ (+1.5) | 0.76 (+0.96) | 0.35 (+0.65) | **3.11** |

Ranking matches intuition: the exact pop/happy/high-energy/non-acoustic track wins clearly. Note "indie pop" does not match "pop" — genre matching is exact-string, not substring/fuzzy.
