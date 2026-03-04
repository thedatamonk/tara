from datetime import datetime
from typing import Optional

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


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    preferred_language: str = "en"


class PlanetPlacement(BaseModel):
    planet: str
    sign: str
    house: int
    degree: float


class BirthChart(BaseModel):
    planets: list[PlanetPlacement]
    ascendant: str
    houses: dict[int, str]


class ChartFeatures(BaseModel):
    features: list[str]


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class SessionState(BaseModel):
    session_id: str
    birth_details: Optional[BirthDetails] = None
    chart: Optional[BirthChart] = None
    chart_features: Optional[ChartFeatures] = None
    messages: list[Message] = []
    preferred_language: str = "en"


class RetrievalChunk(BaseModel):
    text: str
    metadata: dict = {}
    score: float = 0.0


class ChatResponse(BaseModel):
    session_id: str
    response: str
    zodiac: Optional[str] = None
    context_used: list[str] = []
    retrieval_used: bool = False
