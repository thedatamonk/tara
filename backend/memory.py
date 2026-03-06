import asyncio
import json
from pathlib import Path

from loguru import logger
from openai import AsyncOpenAI

from backend.schemas import Message, SessionMemoryData, SessionState

MEMORY_DIR = Path("memory")
UPDATE_EVERY_N_USER_MESSAGES = 3

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


def _load_memory_from_disk(session_id: str) -> SessionMemoryData:
    path = MEMORY_DIR / f"{session_id}.json"
    if not path.exists():
        return SessionMemoryData()
    try:
        data = json.loads(path.read_text())
        return SessionMemoryData(**data)
    except Exception as e:
        logger.warning("Failed to load memory for {sid}: {err}", sid=session_id, err=e)
        return SessionMemoryData()


def _save_memory_to_disk(session_id: str, memory: SessionMemoryData) -> None:
    MEMORY_DIR.mkdir(exist_ok=True)
    path = MEMORY_DIR / f"{session_id}.json"
    path.write_text(memory.model_dump_json(indent=2))
    logger.debug("Saved memory to disk for session {sid}", sid=session_id)


def get_memory(session: SessionState) -> SessionMemoryData:
    """Get memory from session, loading from disk on first access."""
    if session.memory is None:
        session.memory = _load_memory_from_disk(session.session_id)
    return session.memory


def memory_is_empty(memory: SessionMemoryData) -> bool:
    return not memory.user_concerns and not memory.conversation_summary


_SUMMARIZE_PROMPT = """\
You are a conversation memory summarizer. Given existing memory (if any) and recent messages, produce an updated memory object.

Rules:
- `user_concerns`: A short list of the user's recurring topics/concerns (max 5). Merge similar concerns. Drop concerns that seem resolved or one-off.
- `conversation_summary`: A 2-3 sentence summary of the conversation so far. Focus on what was discussed and any key insights given.

Respond with ONLY valid JSON matching this schema:
{"user_concerns": ["..."], "conversation_summary": "..."}
"""


async def _update_memory(
    session: SessionState,
    messages: list[Message],
) -> None:
    current = get_memory(session)

    existing = ""
    if not memory_is_empty(current):
        existing = (
            f"Existing memory:\n"
            f"User concerns: {', '.join(current.user_concerns)}\n"
            f"Summary: {current.conversation_summary}\n\n"
        )

    recent = "\n".join(f"{m.role}: {m.content}" for m in messages[-(UPDATE_EVERY_N_USER_MESSAGES * 2):])

    try:
        response = await _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SUMMARIZE_PROMPT},
                {"role": "user", "content": f"{existing}Recent messages:\n{recent}"},
            ],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        updated = SessionMemoryData(**data)

        # Update both in-memory state and disk
        session.memory = updated
        _save_memory_to_disk(session.session_id, updated)

        logger.info("Memory updated for session {sid}: {concerns}",
                     sid=session.session_id, concerns=updated.user_concerns)
    except Exception as e:
        logger.error("Memory update failed for {sid}: {err}", sid=session.session_id, err=e)


def maybe_trigger_memory_update(session: SessionState) -> None:
    messages = session.messages
    user_count = sum(1 for m in messages if m.role == "user")
    if user_count < UPDATE_EVERY_N_USER_MESSAGES or user_count % UPDATE_EVERY_N_USER_MESSAGES != 0:
        return

    logger.info("Triggering background memory update for session {sid} ({n} user messages)",
                sid=session.session_id, n=user_count)
    asyncio.create_task(_update_memory(session, messages))
