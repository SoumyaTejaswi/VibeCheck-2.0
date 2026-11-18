# VibeCheck 2.0

I extended a music recommendation prototype into a Python command-line tool that ranks tracks by genre, mood, energy, and acoustic preference. The app explains its recommendations, respects explicit-content preferences, and warns listeners when the eligible catalog can only partially match a request. The documented run passed 10 automated tests.

[Explore the code, demo commands, and test results](https://github.com/SoumyaTejaswi/VibeCheck-2.0)

## What this project says about me as an AI engineer

I want people to understand a recommendation and be able to reproduce the evidence behind it. In VibeCheck, I checked that equivalent inputs produce identical rankings, that explicit tracks stay out when excluded, and that invalid energy values stop the request. Working with a small catalog taught me to show users which preferences the system could satisfy. Automated tests helped me verify ranking behavior. I would use listener feedback to evaluate how useful the recommendations are.
