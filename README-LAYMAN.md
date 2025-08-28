# Your AI Doc Assistant — Simple Explanation (What we built & what's next)

This project is a **question-answering assistant for your own files**. You put a few documents into a folder, the app reads and indexes them, and then you can **ask questions** like “What is the renewal grace period?” The assistant answers **only from those files** and shows **citations** so you can trust the result. If it’s unsure, it **abstains** instead of guessing.

---

## What it does *today* (plain English)
- **Reads your docs** in `data/docs/` (we included a sample policy + FAQ).
- **Builds a mini “search brain”** from those docs (indexing).
- **Answers your questions with sources** (citations like `[1]`, `[2]`).
- **Doesn’t make stuff up**: it **abstains** (“I don’t know based on the provided context”) when the answer isn’t in your files or evidence is weak.
- **Works with an online AI model** (Groq, OpenAI) or a **local** one (Ollama). You chose Groq.
- Has a tiny **quality checker** (a “judge”) that flags weak answers.

### How you use it (3 steps)
1. **Add files** to `data/docs/` (start with `.txt` or `.md`).  
2. **Build the index**: `python -m scripts.bootstrap_index`  
3. **Run the server**: `uvicorn app.main:app --reload` and open **http://localhost:8000/docs** to ask via `/ask`.

---

## What we changed recently (non-technical)
- Fixed environment setup so your API key is read from the `.env` file.
- Added **guardrails**: the assistant will now politely say “I don’t know” for chit-chat or off-topic questions.
- Forced **citations** in every answer; if missing, it abstains.
- You confirmed everything works by asking “What is the renewal grace period?” and got a grounded answer.

---

## What you can add next (choose your path)
- **Sharper answers**: add a *re-ranker* that pushes the most relevant evidence to the top.
- **Truth filter**: add a *faithfulness (NLI) check* that blocks answers not backed by the text.
- **Faster & cheaper**: caching for repeated questions; use lighter models for simple queries.
- **Better UI**: a small web page that shows the answer **side-by-side** with highlighted evidence.
- **More file types**: PDFs, tables, emails.
- **Train it a bit** (LoRA/QLoRA): teach the assistant your tone or formats (e.g., always answer in JSON).
- **Deploy**: run on a small VM, Fly.io/Vercel, or behind Nginx for your team.

> You don’t need to do all of these. Pick one improvement, add it, and test. Each step builds confidence.

---

## Safety & privacy in simple terms
- Answers come **only** from your documents.  
- If the content isn’t there, it **doesn’t guess**.  
- Your API keys live in a **local `.env`** file (don’t share it or commit it).

---

## Common gotchas (and fixes)
- **Server returns 500** → Most often the API key wasn’t loaded. Ensure `.env` has `PROVIDER=groq` and your `GROQ_API_KEY`, then restart the server.  
- **No answer for “hello”** → Good! The assistant only answers from your docs.  
- **Added new files but no changes** → Re-run the indexing step to refresh the search brain.

---

## What success looks like
- You ask a real question from your documents and get a **short, correct answer** with **clear citations**.
- The assistant **abstains** on anything it cannot support with your files.

