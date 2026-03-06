from agents import Agent, Runner, RunContextWrapper, function_tool
from loguru import logger

from backend.chart_context import (
    build_resolved_context,
    resolve_classification,
    track_source,
)
from backend.prompts import CLASSIFY_PROMPT
from backend.retrieval import query as retrieval_query
from backend.schemas import AstroClassification, AstroEntity, BirthChart


@function_tool
def retrieve_astrology_knowledge(entities: list[AstroEntity]) -> str:
    """Look up meanings of planets, zodiac signs, or houses.

    For compound queries like "Mars in Aries", pass BOTH entities:
      entities: [{"entity_type": "planet", "entity_name": "Mars"},
                 {"entity_type": "sign", "entity_name": "Aries"}]

    Args:
        entities: List of entities to look up. Each has entity_type and entity_name.
    """
    parts = []
    for entity in entities:
        chunks = retrieval_query(entity.entity_name, entity_type=entity.entity_type,
                                 entity_name=entity.entity_name, n_results=1)
        if chunks:
            track_source(chunks[0].metadata.get("source", ""))
            parts.append(chunks[0].text)
        else:
            parts.append(f"No knowledge found for {entity.entity_type} '{entity.entity_name}'.")
    return "\n\n".join(parts)


@function_tool
async def get_chart_context(ctx: RunContextWrapper[dict], user_message: str) -> str:
    """Analyze a user's astrology question and return their relevant chart placements with meanings.

    Call this tool when the user asks an astrology question (career, relationships, money, health).
    Do NOT call for greetings, casual chat, or emotional venting.

    Args:
        user_message: The user's question, rephrased if needed to be self-contained
                      (include topic context from the conversation).

    Returns:
        Formatted context with planet/sign/house meanings, or empty string if not astro-related.
    """
    chart: BirthChart | None = ctx.context.get("chart")
    if not chart:
        return ""

    classification = await _classify_message(user_message)
    logger.info("Classified: domain={d}, planets={p}, houses={h}",
                d=classification.domain, p=classification.relevant_planets,
                h=classification.relevant_houses)

    if classification.domain == "non-astrology":
        return ""

    resolved = resolve_classification(classification, chart)
    logger.info("Resolved planets: {r}", r=resolved)

    chart_context = build_resolved_context(resolved, classification.domain, user_message)
    return chart_context


async def _classify_message(user_message: str) -> AstroClassification:
    agent = Agent(
        name="AstroClassifier",
        instructions=CLASSIFY_PROMPT,
        model="gpt-4o-mini",
        output_type=AstroClassification,
    )
    result = await Runner.run(agent, input=user_message)
    logger.debug("Classification: {c}", c=result.final_output)
    return result.final_output
