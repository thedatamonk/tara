from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend import session_manager
from backend.astrology_engine import generate_chart, generate_chart_svg
from backend.llm_agent import generate_response
from backend.retrieval import init_retrieval
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

        svg = generate_chart_svg(details)
        session.chart_svg = svg
    except Exception as e:
        logger.error("Chart generation failed: {err}", err=e)
        raise HTTPException(status_code=400, detail=f"Chart generation failed: {e}")

    # Static greeting — no LLM call needed
    greeting = f"Namaste {details.name}!"

    # Store greeting in session
    session_manager.add_message(session.session_id, "assistant", greeting)

    logger.info("Chart created for session {sid}", sid=session.session_id)

    return CreateChartResponse(
        session_id=session.session_id,
        chart_svg=svg,
        zodiac=chart.ascendant,
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

    # LLM response (agent handles retrieval internally via tool)
    result = await generate_response(
        user_message=req.message,
        messages=session.messages,
        preferred_language=req.preferred_language,
        birth_details=session.birth_details,
        chart=session.chart,
    )

    # Record assistant message
    session_manager.add_message(session.session_id, "assistant", result.text)

    # Determine zodiac from Sun sign
    sun = next((p for p in session.chart.planets if p.planet == "Sun"), None)
    zodiac = sun.sign if sun else session.chart.ascendant

    chat_response = ChatResponse(
        session_id=session.session_id,
        response=result.text,
        zodiac=zodiac,
        context_used=result.retrieval_sources,
        retrieval_used=result.retrieval_used,
    )
    logger.info("ChatResponse: {r}", r=chat_response.model_dump())
    return chat_response
