import uuid
from datetime import datetime, timezone

from loguru import logger

from backend.schemas import (
    BirthChart,
    BirthDetails,
    ChartFeatures,
    Message,
    SessionState,
)

_sessions: dict[str, SessionState] = {}


def create_session(preferred_language: str = "en") -> SessionState:
    session_id = str(uuid.uuid4())
    session = SessionState(session_id=session_id, preferred_language=preferred_language)
    _sessions[session_id] = session
    logger.info("Created session {session_id}", session_id=session_id)
    return session


def get_session(session_id: str) -> SessionState | None:
    return _sessions.get(session_id)


def add_message(session_id: str, role: str, content: str) -> None:
    session = _sessions.get(session_id)
    if not session:
        logger.warning("Session {session_id} not found", session_id=session_id)
        return
    session.messages.append(
        Message(role=role, content=content, timestamp=datetime.now(timezone.utc))
    )


def set_birth_details(session_id: str, details: BirthDetails) -> None:
    session = _sessions.get(session_id)
    if session:
        session.birth_details = details


def set_chart(session_id: str, chart: BirthChart) -> None:
    session = _sessions.get(session_id)
    if session:
        session.chart = chart


def set_chart_features(session_id: str, features: ChartFeatures) -> None:
    session = _sessions.get(session_id)
    if session:
        session.chart_features = features
