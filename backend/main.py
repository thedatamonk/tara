from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend import session_manager
from backend.astrology_engine import generate_chart, generate_chart_svg
from backend.feature_extractor import extract_features
from backend.llm_agent import generate_response, needs_retrieval
from backend.retrieval import init_retrieval, query as retrieval_query
from backend.schemas import (
    BirthDetails,
    ChatRequest,
    ChatResponse,
    CreateChartRequest,
    CreateChartResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_retrieval()
    yield


app = FastAPI(title="Tara — Astro Insight Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/create_astro_chart", response_model=CreateChartResponse)
async def create_astro_chart(req: CreateChartRequest):
    profile = req.user_profile

    # Create session
    session = session_manager.create_session(preferred_language=profile.preferred_language)

    # Store birth details
    details = BirthDetails(
        name=profile.name,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        birth_place=profile.birth_place,
    )
    session_manager.set_birth_details(session.session_id, details)

    # Generate chart
    try:
        chart = generate_chart(details)
        session_manager.set_chart(session.session_id, chart)

        features = extract_features(chart)
        session_manager.set_chart_features(session.session_id, features)

        svg = generate_chart_svg(details)
        session.chart_svg = svg
    except Exception as e:
        logger.error("Chart generation failed: {err}", err=e)
        raise HTTPException(status_code=400, detail=f"Chart generation failed: {e}")

    # Retrieve relevant chunks using features
    feature_list = features.features
    chunks = retrieval_query(feature_list, " ".join(feature_list))
    context_used = list({c.metadata.get("source", "") for c in chunks if c.metadata.get("source")})

    # Generate initial greeting
    greeting = await generate_response(
        user_message="[new session]",
        messages=session.messages,
        chart_features=features,
        chunks=chunks,
        preferred_language=session.preferred_language,
        birth_details=details,
    )

    # Store greeting in session
    session_manager.add_message(session.session_id, "assistant", greeting)

    logger.info("Chart created for session {sid}", sid=session.session_id)

    return CreateChartResponse(
        session_id=session.session_id,
        chart_svg=svg,
        zodiac=chart.ascendant,
        features=feature_list,
        context_used=context_used,
        greeting=greeting,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session = session_manager.get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.chart is None:
        raise HTTPException(status_code=400, detail="Chart not generated — use /create_astro_chart first")

    # Record user message
    session_manager.add_message(session.session_id, "user", req.message)

    # Retrieval (intent-based)
    chunks = []
    context_used = []
    retrieval_used = False
    if needs_retrieval(req.message, has_chart=True):
        feature_list = session.chart_features.features if session.chart_features else []
        chunks = retrieval_query(feature_list, req.message)
        retrieval_used = bool(chunks)
        context_used = list({c.metadata.get("source", "") for c in chunks if c.metadata.get("source")})

    # LLM response
    answer = await generate_response(
        user_message=req.message,
        messages=session.messages,
        chart_features=session.chart_features,
        chunks=chunks,
        preferred_language=req.preferred_language,
        birth_details=session.birth_details,
    )

    # Record assistant message
    session_manager.add_message(session.session_id, "assistant", answer)

    return ChatResponse(
        session_id=session.session_id,
        response=answer,
        context_used=context_used,
        retrieval_used=retrieval_used,
    )
