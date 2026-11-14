## This is the Output given by Claude AI when I asked it to research about how recommendation systems work!

# How Spotify & YouTube Predict What You'll Like Next

*As of October 27, 2026*

## What "recommending" means

Every time Spotify queues up the next song, or YouTube fills your homepage, a **recommender system** is predicting what you're likely to enjoy from data it already has — about you, and about the available songs or videos.

Two building blocks show up across almost every large recommender, including Spotify's and YouTube's:

- **Collaborative filtering** predicts your taste from what *other people* with similar behavior liked.
- **Content-based filtering** predicts your taste from the *attributes* of the songs or videos themselves (genre, tempo, topic, and so on).

Neither company publishes its full, current production algorithm — those details are trade secrets. This guide draws on official sources where they exist (YouTube's own help pages, a published Google research paper, Spotify's developer documentation) and flags anything drawn from secondary analysis, academic papers, or general industry patterns rather than a platform's own statement.

## Collaborative filtering: learning from other listeners

**Collaborative filtering (CF)** recommends an item based on patterns across many users' behavior — not on anything about the item's content. Its core assumption: people who agreed in the past will probably agree again.

**Simple example:** Users A and B have both streamed heavily from Artists X, Y, and Z. User A also listens to Artist W, which B hasn't tried. Because A and B overlap so much on X, Y, and Z, the system infers they have similar taste and recommends W to B — even though W shares no obvious genre or sound with X, Y, or Z.

**How this shows up at YouTube (documented):** Google's 2016 research paper *"Deep Neural Networks for YouTube Recommendations"* (Covington, Adams, and Sargin) describes a two-stage system. The first stage, *candidate generation*, narrows YouTube's entire catalog down to a few hundred videos using signals like a viewer's watch history and search terms compared against other viewers — a collaborative-filtering-style step. A second *ranking* network then scores those candidates, trained to predict expected watch time rather than clicks, specifically to avoid rewarding clickbait. YouTube's own support documentation adds that signals like watch history, likes, shares, and "not interested" feedback from the whole user base feed into what gets recommended.

**How this shows up at Spotify (mixed sourcing):** A 2025 Spotify Research post (via a secondary Redis engineering write-up) describes learning track relationships from *playlist co-occurrence* — songs that many different users place in playlists together are inferred to be related, independent of genre or audio. Former Spotify engineer Erik Bernhardsson has also published slides describing matrix factorization over listening data to find latent "taste" patterns. Specific claims about a model called "ELSA" powering this today come only from third-party blogs and could not be confirmed against a current Spotify source, so treat that detail as unverified.

## Content-based filtering: learning from the content itself

**Content-based filtering** predicts whether you'll like an item by comparing its *attributes* to the attributes of items you've already liked — no other users required. For music, attributes might be genre, tempo (beats per minute), mood, energy, or instrumentation. For video, they might be topic, spoken-word transcript, or on-screen text.

**Simple example:** If you mostly play fast, high-energy electronic tracks, a content-based system looks for other tracks that measure similarly on tempo and energy — even if no other listener has ever connected those songs to each other.

**How this shows up at Spotify (documented, with a caveat):** Spotify's developer platform historically published a *Get Audio Features* endpoint exposing per-track scores such as danceability, energy, valence (a measure of musical positivity/mood), tempo, acousticness, and instrumentalness — the kind of attributes a content-based system would compare across songs. On November 27, 2024, Spotify removed most developers' access to this and several related endpoints (reported by TechCrunch); the features still exist inside Spotify's own systems, but outside developers can no longer query them the way researchers once did. An academic study (*Psychologically-Inspired Music Recommendation System*, arXiv 2022) used these public features to show that valence in particular tracks a listener's mood better than genre does.

**How this shows up at YouTube (general pattern, not YouTube-confirmed):** YouTube doesn't publish a numeric feature set for videos the way Spotify did for songs. Its own documentation says recommendations weigh a video's topic and subject matter alongside viewer behavior, but doesn't detail the content features used. Industry practice generally extracts signals like category, title/description text, and spoken-word transcripts for this purpose — this is a standard technique, not a confirmed description of YouTube's internals.

## Comparing the two methods

| | Collaborative filtering | Content-based filtering |
| --- | --- | --- |
| Data it needs | Behavior across many users: plays, watch time, likes, skips, shares | Attributes of the item itself: genre, tempo, mood/audio features; topic, transcript, description |
| Strengths | Can surface surprising items with no obvious content similarity; improves as more people use the platform | Works without needing any other users; recommendations are easy to explain ("because it's similar tempo/genre to X") |
| Limitations | Needs a lot of behavior data to find reliable patterns; can get stuck in feedback loops recommending more of the same | Tends to stay inside a user's existing taste — less likely to surprise them; depends on having rich, accurate item attributes |
| New users | Struggles — no behavior history yet to match against other users ("cold start") | Can start immediately once a user states or shows even one preference, since item attributes already exist |
| New content | Struggles — no one has interacted with it yet, so it has no behavioral signal | Works right away — a new item's attributes can be compared to others as soon as it's added |

## Combining both: hybrid recommendation systems

A **hybrid recommender** blends collaborative and content-based signals so each one covers the other's weak spot: content-based filtering handles new users and new items (cold start), while collaborative filtering supplies the serendipity — surprising-but-good picks — that content similarity alone can't find.

**At YouTube (documented):** the Covington et al. system already blends both kinds of signal in one pipeline — the candidate-generation network behaves like collaborative filtering (comparing viewers to each other), while the ranking network folds in contextual and content signals (such as a video's topic and recency) alongside behavioral ones, then optimizes for expected watch time.

**At Spotify (described across secondary sources, consistently):** write-ups of Discover Weekly and similar Spotify features describe three kinds of models working together: a collaborative-filtering model over listening/playlist data, a natural-language model that reads text written about artists and songs (reviews, articles, metadata) to place them in a "taste space," and an audio model that analyzes the raw sound of a track. Because no single current Spotify engineering post lays this out end to end, treat the specific three-model architecture as a well-corroborated secondary description rather than an official statement.

**Why hybrids matter for cold start:** academic literature on recommender systems consistently frames cold start — making good recommendations for a brand-new user or brand-new item with no interaction history — as collaborative filtering's central weakness, and content-based signals as the standard fix, since a new song or video already has attributes to compare even before anyone has watched or played it.

## Sources

**Official / primary**

- [Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/pub45530) — Covington, Adams & Sargin, Google Research, 2016
- [How YouTube recommendations work](https://support.google.com/youtube/answer/16089387) — YouTube Help
- [How YouTube recommends videos (PDF)](https://services.google.com/fh/files/misc/how-youtube-recommends-videos.pdf) — Google
- [YouTube recommendations — How YouTube Works](https://www.youtube.com/howyoutubeworks/product-features/recommendations) — YouTube
- [Spotify Web API — Get Track's Audio Features](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/) — Spotify (access now restricted for most developers since Nov 2024)

**Secondary / analysis (used with attribution in the text above)**

- [Spotify cuts developer access to several of its recommendation features](https://techcrunch.com/2024/11/27/spotify-cuts-developer-access-to-several-of-its-recommendation-features/) — TechCrunch, Nov 27, 2024
- [How YouTube Recommendation Works](https://www.infoq.com/news/2016/09/How-YouTube-Recommendation-Works) — InfoQ, 2016
- [Collaborative filtering: How to build a recommender system](https://redis.io/blog/collaborative-filtering-how-to-build-a-recommender-system) — Redis Engineering (cites Spotify Research's playlist co-occurrence work)
- [Music recommendations at Spotify](https://www.slideshare.net/erikbern/collaborative-filtering-at-spotify-16182818) — Erik Bernhardsson, former Spotify engineer
- [Inside the content recommendation engine at the heart of Spotify](https://exchange.scale.com/public/blogs/inside-the-content-recommendation-engine-at-the-heart-of-spotify) — Scale AI
- [Psychologically-Inspired Music Recommendation System](https://arxiv.org/pdf/2205.03459) — arXiv, 2022
- [Collaborative filtering](https://xenoss.io/ai-and-data-glossary/collaborative-filtering) — Xenoss AI & Data Glossary (general definitions)

*Neither Spotify nor YouTube publishes its full current production algorithm; claims above are labeled documented, mixed-sourced, or general industry pattern based on the strength of the source behind them.*

## Soumya's Findings from the document 
# Data Types Identified : Collaborative filtering : Plays,Likes,Skips,playlist,search terms. Content based Filtering : genre,Category