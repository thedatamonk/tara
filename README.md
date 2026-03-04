# Mynaksh

A conversational Vedic astrology agent. You give it your birth details, it builds your chart, and then you can chat with it about career, relationships, finances — whatever's on your mind. It remembers context across turns and pulls in astrological knowledge when needed.

## Setup

You need Python 3.11+ and Node.js.

```bash
# Backend
uv sync
cp .env.example .env  # add your OPENAI_API_KEY
uv run uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## How it works

| Capability | How |
|---|---|
| **Birth chart computation** | Kerykeion library computes planetary positions, houses, and aspects from birth details |
| **Personalized responses** | Chart features (zodiac sign, moon sign, dashas) are extracted and injected into every LLM prompt |
| **Knowledge grounding (RAG)** | ChromaDB vector store with astrological texts — retrieved only when the query actually needs it |
| **Multi-turn memory** | Session manager tracks conversation history with windowing to control context growth |
| **Hindi + English** | Language preference is passed per request; the agent responds entirely in the chosen language |
| **Conversational tone** | System prompt is tuned for short, warm, one-insight-at-a-time responses — not textbook dumps |

## API

Single endpoint: `POST /chat`

**Request** — all fields optional except on first call (where you'd send `user_profile`):

```json
{
  "session_id": "abc-123",
  "message": "How will my career be this month?",
  "preferred_language": "en",
  "user_profile": {
    "name": "Ritika",
    "birth_date": "1995-08-20",
    "birth_time": "14:30",
    "birth_place": "Jaipur, India",
    "preferred_language": "hi"
  }
}
```

- `session_id` — omit on first call, one gets created for you
- `message` — omit to get an initial greeting
- `user_profile` — only needed on first call to set up the chart

**Response:**

```json
{
  "session_id": "abc-123",
  "response": "आपके लिए यह महीना अवसर लेकर आ रहा है...",
  "zodiac": "Leo",
  "context_used": ["career_guidance", "leo_traits"],
  "retrieval_used": true
}
```

## Stack

- **Backend**: FastAPI + OpenAI Agents SDK (gpt-4o-mini)
- **Frontend**: React + Vite
- **Vector store**: ChromaDB
- **Astro engine**: [Kerykeion](https://kerykeion.net/)
