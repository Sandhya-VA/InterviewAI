# InterviewAI

**1st Prize — Vanderbilt Immersion Showcase 2025** (40+ teams)

Mock interview platform that uses an agentic LLM pipeline to ask skill-specific questions, transcribe your spoken answers, and evaluate them with context from earlier in the same session.

---

## The idea

Most interview prep tools give you a static question list. InterviewAI parses your resume to extract your actual skills, generates targeted questions per skill, then evaluates your spoken answers using Mistral — with full session memory so the model knows what you said earlier.

Upload your resume, pick a role, start talking.

---

## Stack

- **Frontend** — React (Vite)
- **Backend** — Flask REST API
- **LLM** — Mistral via Ollama (local, no API costs)
- **Speech-to-text** — OpenAI Whisper (medium model)
- **Resume parsing** — SpaCy with custom NER model trained on tech skill entities
- **Vector store / RAG** — ChromaDB with `sentence-transformers` (all-MiniLM-L6-v2)

---

## How the RAG pipeline works

Each Q&A exchange is embedded using `sentence-transformers` and stored in a per-session ChromaDB collection. Before evaluating each answer, the backend does a semantic similarity search against the session history — retrieving the most relevant prior exchanges as context for the LLM. This means the evaluator notices patterns across the session: if you consistently struggled with concurrency questions, the final feedback reflects that, not just the last answer.

```
Resume PDF
    |
SpaCy NER → skill list
    |
Mistral → 5 questions per skill
    |
User speaks answer → Whisper → transcription
    |
sentence-transformers → embed exchange → ChromaDB (per-session collection)
    |
RAG retrieval: query ChromaDB for relevant past context
    |
Mistral → evaluate answer + score (with retrieved context)
    |
Final summary: RAG retrieval → Mistral → overall feedback
```

---

## Setup

Requires Ollama running locally:
```bash
ollama pull mistral
```

Backend:
```bash
cd InterviewAI_Frontend
pip install -r requirements.txt
python -m spacy download en_core_web_md

# Set model path in .env
cp .env.example .env

python app.py
```

Frontend:
```bash
cd InterviewAI_Frontend/frontend
npm install
npm run dev
```

---

## Why we built the eval harnesses

Getting Mistral to score consistently was the hardest part. A correct answer phrased differently from what the model expected would get unfairly penalized. We built evaluation harnesses — a set of known Q&A pairs with expected score ranges — and ran them after every prompt change to catch regressions before they hit users.

---

`python` `flask` `react` `whisper` `mistral` `ollama` `chromadb` `rag` `sentence-transformers` `spacy` `nlp`
