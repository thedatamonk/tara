from agents import Agent, Runner
from loguru import logger

from backend.chart_context import pop_retrieval_sources
from backend.memory import memory_is_empty
from backend.prompts import SYSTEM_PROMPT
from backend.schemas import BirthChart, BirthDetails, LLMResult, Message, SessionMemoryData
from backend.tools import get_chart_context, retrieve_astrology_knowledge


def _build_memory_section(memory: SessionMemoryData | None) -> str:
    if not memory or memory_is_empty(memory):
        return ""
    parts = ["<memory>"]
    if memory.user_concerns:
        parts.append(f"User's recurring concerns: {', '.join(memory.user_concerns)}")
    if memory.conversation_summary:
        parts.append(f"Conversation so far: {memory.conversation_summary}")
    parts.append("</memory>")
    return "\n".join(parts)


def _build_birth_details_section(birth_details: BirthDetails | None) -> str:
    if not birth_details:
        return ""
    return (
        "User's Birth Details:\n"
        f"- Name: {birth_details.name}\n"
        f"- Date of Birth: {birth_details.birth_date}\n"
        f"- Time of Birth: {birth_details.birth_time}\n"
        f"- Place of Birth: {birth_details.birth_place}"
    )


def _build_message_history(messages: list[Message]) -> list[dict]:
    return [{"role": msg.role, "content": msg.content} for msg in messages]


async def generate_response(
    user_message: str,
    messages: list[Message],
    preferred_language: str = "en",
    birth_details: BirthDetails | None = None,
    chart: BirthChart | None = None,
    memory: SessionMemoryData | None = None,
) -> LLMResult:
    birth_details_section = _build_birth_details_section(birth_details)
    memory_section = _build_memory_section(memory)

    language_name = "Hindi" if preferred_language == "hi" else "English"
    system_prompt = SYSTEM_PROMPT.format(
        language_name=language_name,
        birth_details_section=birth_details_section,
        memory_section=memory_section,
    )

    agent = Agent(
        name="AstroAgent",
        instructions=system_prompt,
        model="gpt-4o-mini",
        tools=[get_chart_context, retrieve_astrology_knowledge],
    )

    input_messages = _build_message_history(messages)
    input_messages.append({"role": "user", "content": user_message})

    logger.info("Calling LLM with {n} messages, language={lang}",
                n=len(input_messages), lang=preferred_language)

    # Clear any stale sources before the run
    pop_retrieval_sources()

    result = await Runner.run(agent, input=input_messages, context={"chart": chart})

    sources = pop_retrieval_sources()
    return LLMResult(
        text=result.final_output,
        retrieval_sources=sources,
        retrieval_used=len(sources) > 0,
    )
