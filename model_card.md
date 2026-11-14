# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Think of it less like a smart AI and more like a judge scoring a competition: every song in the catalog gets compared one at a time against a user's stated tastes, and whichever songs score the highest win a spot in the top 5.

A user's "taste profile" is just four preferences: a favorite genre, a favorite mood, a target energy level (how mellow or intense they want the music to feel), and whether or not they like acoustic-sounding tracks.

For each song, the model checks four things and hands out points for each one it gets right:

- **Genre** — does the song's genre exactly match the user's favorite? If so, it earns the single biggest chunk of points. Close genres don't count — "indie pop" is not the same as "pop" as far as the model is concerned.
- **Mood** — does the song's mood (happy, chill, intense, etc.) exactly match what the user said they wanted? This is worth a good amount of points, just slightly less than genre.
- **Energy** — rather than a strict yes/no, this one is a sliding scale. A song earns the most points when its energy is exactly what the user asked for, and it loses points gradually the further away it drifts in either direction.
- **Acoustic feel** — similarly a sliding scale: songs that lean more acoustic score higher for users who said they like acoustic music, and songs that lean less acoustic score higher for users who said they don't.

All four of these points get added together into one final number, and the songs are then lined up from highest score to lowest. The top five highest-scoring songs are what gets recommended. Genre and mood matter most because they are what the user explicitly told the system they want, while energy and acoustic feel act as smaller tiebreakers that fine-tune the ranking.

Alongside each recommended song, the model also writes out the specific reasons it scored well — for example, "matches your favorite genre" or "energy closely matches your target" — so a user can see exactly why a song was picked rather than just trusting a mystery number.

Compared to the starter logic (which just returned the first few songs in the file with no real scoring at all), this is the first version of the system that actually reads the user's preferences and ranks the catalog against them.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
