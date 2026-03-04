from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend import session_manager
from backend.astrology_engine import generate_chart, generate_chart_svg
from backend.feature_extractor import extract_features
from backend.llm_agent import generate_response, needs_retrieval
from backend.retrieval import query as retrieval_query
from backend.schemas import BirthDetails, ChatRequest, ChatResponse

app = FastAPI(title="Tara — Astro Insight Agent")

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


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Resolve or create session
    session = None
    if req.session_id:
        session = session_manager.get_session(req.session_id)

    if session is None:
        lang = req.preferred_language
        if req.user_profile:
            lang = req.user_profile.preferred_language
        session = session_manager.create_session(preferred_language=lang)

    # Update language preference if provided
    if req.user_profile:
        session.preferred_language = req.user_profile.preferred_language

    # Store birth details from user_profile if provided and not already set
    if req.user_profile and session.birth_details is None:
        details = BirthDetails(
            name=req.user_profile.name,
            birth_date=req.user_profile.birth_date,
            birth_time=req.user_profile.birth_time,
            birth_place=req.user_profile.birth_place,
        )
        session_manager.set_birth_details(session.session_id, details)
        session.birth_details = details

    # Generate chart if we have birth details but no chart yet
    zodiac = None
    if session.birth_details and session.chart is None:
        try:
            chart = generate_chart(session.birth_details)
            session_manager.set_chart(session.session_id, chart)
            session.chart = chart

            features = extract_features(chart)
            session_manager.set_chart_features(session.session_id, features)
            session.chart_features = features

            svg = generate_chart_svg(session.birth_details)
            session.chart_svg = svg

            zodiac = chart.ascendant
            logger.info("Chart and features generated for session {sid}",
                        sid=session.session_id)
        except Exception as e:
            logger.error("Chart generation failed: {err}", err=e)
            raise HTTPException(status_code=400, detail=f"Chart generation failed: {e}")

    if session.chart:
        zodiac = session.chart.ascendant

    # Determine the user message for LLM input
    is_initial_greeting = req.message is None
    user_message = req.message or "[new session]"

    # Record user message (skip internal trigger)
    if not is_initial_greeting:
        session_manager.add_message(session.session_id, "user", user_message)

    # Retrieval (intent-based)
    chunks = []
    context_used = []
    retrieval_used = False
    if not is_initial_greeting and needs_retrieval(user_message, has_chart=session.chart is not None):
        feature_list = session.chart_features.features if session.chart_features else []
        chunks = retrieval_query(feature_list, user_message)
        retrieval_used = bool(chunks)
        context_used = list({c.metadata.get("source", "") for c in chunks if c.metadata.get("source")})

    # LLM response
    answer = await generate_response(
        user_message=user_message,
        messages=session.messages,
        chart_features=session.chart_features,
        chunks=chunks,
        preferred_language=session.preferred_language,
        birth_details=session.birth_details,
    )

    # Record assistant message
    session_manager.add_message(session.session_id, "assistant", answer)

    # Only send SVG on the initial chart generation response
    send_svg = session.chart_svg if is_initial_greeting else None

    return ChatResponse(
        session_id=session.session_id,
        response=answer,
        zodiac=zodiac,
        chart_svg=send_svg,
        context_used=context_used,
        retrieval_used=retrieval_used,
    )
