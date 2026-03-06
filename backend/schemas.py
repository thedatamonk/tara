from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class BirthDetails(BaseModel):
    name: str
    birth_date: str
    birth_time: str
    birth_place: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserProfile(BaseModel):
    name: str
    birth_date: str
    birth_time: str
    birth_place: str
    preferred_language: str = "en"


class CreateChartRequest(BaseModel):
    user_profile: UserProfile


class CreateChartResponse(BaseModel):
    session_id: str
    chart_svg: str
    zodiac: str
    greeting: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    preferred_language: str = "en"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    zodiac: str
    context_used: list[str]
    retrieval_used: bool


class PlanetPlacement(BaseModel):
    planet: str
    sign: str
    house: int
    degree: float


class BirthChart(BaseModel):
    planets: list[PlanetPlacement]
    ascendant: str
    houses: dict[int, str]


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class SessionMemoryData(BaseModel):
    user_concerns: list[str] = []
    conversation_summary: str = ""


class SessionState(BaseModel):
    session_id: str
    birth_details: Optional[BirthDetails] = None
    chart: Optional[BirthChart] = None
    chart_svg: Optional[str] = None
    messages: list[Message] = []
    preferred_language: str = "en"
    memory: Optional[SessionMemoryData] = None


class RetrievalChunk(BaseModel):
    text: str
    metadata: dict = {}
    score: float = 0.0


class LLMResult(BaseModel):
    text: str
    retrieval_sources: list[str]
    retrieval_used: bool


class AstroClassification(BaseModel):
    """LLM classification of a user message for astrological relevance."""
    domain: Literal["career", "relationship", "money", "health", "non-astrology"] = "non-astrology"
    relevant_planets: list[str] = []
    relevant_houses: list[int] = []


class AstroEntity(BaseModel):
    entity_type: str  # "planet", "sign", or "house"
    entity_name: str  # e.g. "Sun", "Aries", "Seventh House"


class ResolvedPlanet(BaseModel):
    """A planet from the classification that was confirmed in the natal chart."""
    planet: str
    sign: str
    house: int
