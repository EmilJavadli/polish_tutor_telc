# 🇵🇱 Polish Tutor: 9-month TELC Polski B1 plan

Streamlit app with a true A0 start that builds toward TELC B1 in 39 weeks (273 lessons, ~1 hour/day).
See **PLAN.md** for the full plan (also on the 📅 Plan page in the app).

## Every lesson (all 4 TELC skills)
| Tab | Time | What |
|---|---|---|
| 📖 Reading | 10′ | TELC-type text (e-mail, forum, notices, official text, article, story), slow/normal audio |
| 🎧 Listening | 10′ | separate recording in TELC format (voice messages, dialogue, interview, opinions) + 5 tasks |
| 🔤 Words | 5′ | 8/10/12/15 new words as your level grows |
| 📐 Grammar | 5′ | at most 1 new grammar point, plus spaced review |
| ✏️ Exercises | 10′ | 19 exercises: vocabulary, grammar, TELC *Elementy języka*; answers explained |
| 📝 Writing | 10′ | choose 1 of 2 tasks, examiner feedback: 4 criteria × 5 pts, corrections |
| 🗣️ Speaking | 5′ | TELC part 1/2/3 rotating; record → transcript → feedback (or type) |
| ✅ Quiz | 5′ | 10 hard questions, no answers shown, 80% to pass, retry until you pass |

A lesson is **completed** when exercises, writing and speaking are submitted and the quiz is passed.
Lessons are numbered by plan day, so missing a calendar day never skips a lesson.
Day 7 of every week is a review (same week's words and grammar, no new words).

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# put your keys into .streamlit/secrets.toml (see secrets.toml.example)
streamlit run app.py
```
Old data from the previous version is not compatible: delete the `data/` folder.

## Tests
```bash
python -m unittest discover tests -v
```

## Structure
```
app.py                     UI
curriculum.py              9-month plan + grammar syllabus (edit here, then: python tools/export_plan.py)
config.py                  secrets, models, counts, quiz pass mark
agent/prompts.py           all prompts
agent/lesson_generator.py  2 validated LLM calls (content, practice) with retries
agent/graders.py           exercises, listening, quiz, writing, speaking
agent/llm.py               OpenAI: JSON, chat stream, speech-to-text
agent/tts.py               ElevenLabs: reading + dialogues (2 voices)
agent/tutor_chat.py        tutor chat
storage/repository.py      data/ (lessons, audio, recordings, progress.json)
```


### A0 calibration
- Weeks 1-4: A0 / Pre-A1, 8 words/day, one new grammar focus, 45-80 word reading, guided writing and survival speaking.
- Weeks 5-9: A1, 10 words/day.
- Weeks 10-17: A2, 12 words/day.
- Weeks 18-30: B1 build, 15 words/day.
- Weeks 31-35: B1 consolidation.
- Weeks 36-39: authentic TELC exam training.
TELC task shapes appear early, but B1 difficulty does not.
