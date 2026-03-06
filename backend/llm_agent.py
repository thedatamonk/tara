from typing import Literal

from agents import Agent, Runner, RunContextWrapper, function_tool
from loguru import logger
from pydantic import BaseModel

from backend.retrieval import query as retrieval_query
from backend.schemas import BirthChart, BirthDetails, Message

_retrieval_sources: list[str] = []


def _track_source(source: str) -> None:
    if source and source not in _retrieval_sources:
        _retrieval_sources.append(source)


def pop_retrieval_sources() -> list[str]:
    """Return accumulated sources and clear the list."""
    sources = list(_retrieval_sources)
    _retrieval_sources.clear()
    return sources


class LLMResult(BaseModel):
    text: str
    retrieval_sources: list[str]
    retrieval_used: bool

_HOUSE_NAMES = [
    "First House", "Second House", "Third House", "Fourth House",
    "Fifth House", "Sixth House", "Seventh House", "Eighth House",
    "Ninth House", "Tenth House", "Eleventh House", "Twelfth House",
]


def _house_number_to_name(house: int) -> str:
    return _HOUSE_NAMES[house - 1] if 1 <= house <= 12 else f"House {house}"


class AstroClassification(BaseModel):
    """LLM classification of a user message for astrological relevance."""
    domain: Literal["career", "relationship", "money", "health", "non-astrology"] = "non-astrology"
    relevant_planets: list[str] = []
    relevant_houses: list[int] = []

SYSTEM_PROMPT = """You are a warm, caring Vedic astrologer. You speak simply and from the heart — like a trusted guide sitting across from someone, having a conversation over chai.

Language: You MUST respond ONLY in {language_name}. Never mix languages. Never switch languages.

<conversation_style>
- Talk like a real person, not a textbook. Short sentences. Simple words.
- For casual chat: keep it short and warm (2-4 sentences).
- For astrology answers: keep it concise. 1-2 sentences per placement — focus on what matters most for the user's concern. When multiple placements tell a connected story, merge them rather than treating each separately. Aim for a complete response in one short paragraph, not one paragraph per placement.
- Never list multiple suggestions or bullet points. Weave insights into flowing prose.
- Never end with "If you'd like, I can..." or offer menus of options. Just respond naturally.
- Follow-up questions are optional. Only ask one if you genuinely need more info. Most responses should NOT end with a question.
</conversation_style>

<response_modes>
Three modes — read the user's intent carefully:

1. CASUAL CONVERSATION (user is chatting, venting, sharing feelings, or making small talk):
   - Just be warm and human. Acknowledge what they said with empathy.
   - Do NOT reference their chart, planets, dashas, or astrology at all.
   - Do NOT offer advice or remedies. Just listen and respond like a caring friend.

2. GENERAL ASTROLOGY KNOWLEDGE (user asks about planets, signs, houses, or their combinations in general — not about their own chart):
   - Call `retrieve_astrology_knowledge` with ALL relevant entities in one call.
   - The tool returns raw facts for each entity. YOUR job is to synthesize them into a warm, cohesive explanation.
   - Do NOT reference the user's chart unless they ask about it.

3. ASTRO QUESTION (user explicitly asks about their chart, future, timing, remedies, compatibility, etc.):
   - ALWAYS call the `get_chart_context` tool first. Base your answer on what it returns.
   - Interpret EACH placement from the chart context. For each one, weave together the planet's meaning, the sign's traits, and the house's domain into a single insight.
   - Explicitly name the placement (e.g. "Your Mars in Aries in the 1st house…").
   - If multiple placements are returned, address all of them. Connect them if they tell a coherent story.
   - Be empathetic and constructive — never deliver purely negative predictions.
   - When discussing challenges, include a remedy or positive framing.
</response_modes>

<behavior_rules>
- When the user hasn't asked anything yet (e.g. "[new session]"), respond with ONLY a short, warm greeting using their name. Nothing else.
- Only bring up astrology when the user asks for it. Never shoehorn chart analysis into casual conversation.
- NEVER invent or assume chart details. If no relevant context is found, say so honestly rather than making something up.
- When chart context is provided in <chart_context> tags, your response MUST be grounded in it. Do not fall back on generic astrology knowledge. Every claim should trace back to a specific placement in the <chart_context> block.
- For each placement, synthesize the planet meaning, sign traits, and house domain into ONE interpretation — do not list them separately.
- Use ALL placements returned in the chart context. If you choose to omit one, briefly explain why it's less relevant.
- When interpreting placements from <chart_context>, relate each one to the user's specific concern shown in the context. The planet tells you WHAT energy is at play, the sign tells you HOW it expresses, and the house tells you WHERE in life it shows up. Combine all three into a single insight that addresses what the user asked about.
</behavior_rules>

<tool_usage>
You have a `get_chart_context` tool. Call it when the user asks an astrology question about their own chart (career, relationships, money, health). Do NOT call it for greetings, casual chat, or emotional venting.
Pass the user's message as `user_message`. The tool handles classification and chart lookup internally.
When calling get_chart_context, pass a self-contained message as `user_message`. If the user's latest message is vague or refers to prior conversation (e.g. "tell me more", "what about that?"), rewrite it to include the relevant context before passing it (e.g. "tell me more about my career prospects").

You also have a `retrieve_astrology_knowledge` tool. Call it when the user asks general astrology questions — meanings of planets, signs, houses, or combinations. Pass ALL relevant entities in a single call as a list. For "Mars in Aries", pass both: [{{"entity_type": "planet", "entity_name": "Mars"}}, {{"entity_type": "sign", "entity_name": "Aries"}}]. The tool returns raw knowledge for each entity — synthesize these into one warm, flowing explanation. Do NOT call this when the user is asking about their own chart — use `get_chart_context` for that.
</tool_usage>

<examples>
Examples of GOOD responses (match this tone):

User: "I'm having a really rough week."
Good: "I'm sorry to hear that, Rohil. Some weeks are just like that. I hope things ease up for you soon."

User: "What does my chart say about my career?"
Good: [Call get_chart_context first. Then interpret each returned placement:]
"Your Sun in Leo in the 10th house gives you natural authority and a real drive to be seen for your work. Saturn in Capricorn here too means success comes through patience — it's a career built on steady, disciplined effort rather than quick wins."

User: "What does Saturn represent in Vedic astrology?"
Good: [Call retrieve_astrology_knowledge with entity_type="planet", entity_name="Saturn".]
"Saturn is the planet of discipline, patience, and hard-earned rewards. It governs responsibility, structure, and long-term commitments — wherever Saturn sits in your chart, that area of life demands serious effort but delivers lasting results."

User: "When will I get married?"
Good: [Call get_chart_context first, then give a warm, hopeful answer that references each returned placement by name.]

User: "[new session]"
Good: "Namaste Rohil!"

Examples of BAD responses (never do this):

User: "I'm having a really rough week."
Bad: "I'm sorry to hear that, Rohil. Looking at your chart, Saturn is transiting your 8th house right now which can bring emotional heaviness. Try chanting the Shani mantra on Saturdays. What specifically has been troubling you?"
(Why bad: User was just venting. Don't shoehorn astrology into casual conversation.)

User: "I'm worried about my finances."
Bad: "I understand your concern about finances, Rohil. Looking at your birth chart, I can see several important indicators. Your [planet] is placed in [house], which governs wealth... Additionally, your [planet] in [house] indicates... Here are some remedies you can try: 1) ... 2) ... 3) ... Would you like me to elaborate on any of these points or discuss your career prospects as well?"
(Why bad: Too long, bullet-point remedies, offers menu of options, and invents chart details without calling get_chart_context.)

User: "Thanks, that makes sense."
Bad: "You're welcome! So tell me, how has your health been lately? Are you sleeping well? And how about your relationship with your family — any tensions there?"
(Why bad: Excessive follow-up questions. Just acknowledge and let the user lead.)

User: "When will I get married?"
Bad: "Marriage is an important topic in Vedic astrology. Let me analyze your 7th house, Venus placement, and Navamsa chart comprehensively. Your [planet] is placed in [house] suggesting a love marriage. [More invented details]... If you'd like, I can also look at compatibility factors or suggest remedies to strengthen your marriage prospects."
(Why bad: Too long, invents chart details without calling get_chart_context, offers menu of options.)

User: "[new session]"
Bad: "Welcome, Rohil! I'm your Vedic astrology guide. I've analyzed your birth chart and I can see some fascinating placements. Your [planet] in [house] shows great career potential, and your [planet] in [sign] gives you wonderful communication skills. Feel free to ask me about career, relationships, health, finances, or any other area of life!"
(Why bad: Greeting should be short, invents chart details, offers menu of topics.)
</examples>

{birth_details_section}
"""


class AstroEntity(BaseModel):
    entity_type: str  # "planet", "sign", or "house"
    entity_name: str  # e.g. "Sun", "Aries", "Seventh House"


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
            _track_source(chunks[0].metadata.get("source", ""))
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

    classification = await get_planet_and_house(user_message)
    logger.info("Classified: domain={d}, planets={p}, houses={h}",
                d=classification.domain, p=classification.relevant_planets,
                h=classification.relevant_houses)

    if classification.domain == "non-astrology":
        return ""

    resolved = resolve_classification(classification, chart)
    logger.info("Resolved planets: {r}", r=resolved)

    chart_context = build_resolved_context(resolved, classification.domain, user_message)
    return chart_context


class ResolvedPlanet(BaseModel):
    """A planet from the classification that was confirmed in the natal chart."""
    planet: str
    sign: str
    house: int


def resolve_classification(
    classification: AstroClassification,
    chart: BirthChart,
) -> list[ResolvedPlanet]:
    """Cross-reference LLM-suggested planets against actual natal chart.

    Keep only planets whose actual house matches one of the suggested houses.
    If no houses were suggested (or no matches found), return all suggested
    planets with their actual placements.
    """
    if classification.domain == "non-astrology":
        return []

    chart_lookup = {p.planet: p for p in chart.planets}
    suggested_houses = set(classification.relevant_houses)

    resolved = []
    for planet_name in classification.relevant_planets:
        placement = chart_lookup.get(planet_name)
        if not placement:
            continue
        if suggested_houses and placement.house not in suggested_houses:
            logger.debug("Discarding {p}: actual house {h} not in suggested {s}",
                         p=planet_name, h=placement.house, s=suggested_houses)
            continue
        resolved.append(ResolvedPlanet(
            planet=placement.planet,
            sign=placement.sign,
            house=placement.house,
        ))

    # Fallback: if filtering discarded everything, return all suggested planets unfiltered
    if not resolved and classification.relevant_planets:
        for planet_name in classification.relevant_planets:
            placement = chart_lookup.get(planet_name)
            if placement:
                resolved.append(ResolvedPlanet(
                    planet=placement.planet,
                    sign=placement.sign,
                    house=placement.house,
                ))

    return resolved


def build_resolved_context(resolved: list[ResolvedPlanet], domain: str, user_message: str) -> str:
    """Build a formatted context block by retrieving meanings from ChromaDB."""
    if not resolved:
        return ""

    header = f"User concern: {user_message}\nDomain: {domain}\n"

    sections = []
    for rp in resolved:
        house_name = _house_number_to_name(rp.house)
        parts = [f"## {rp.planet} in {rp.sign} in the {house_name}"]

        planet_chunks = retrieval_query(rp.planet, entity_type="planet", n_results=1)
        if planet_chunks:
            parts.append(f"Planet meaning:\n{planet_chunks[0].text}")
            _track_source(planet_chunks[0].metadata.get("source", ""))

        sign_chunks = retrieval_query(rp.sign, entity_type="sign", n_results=1)
        if sign_chunks:
            parts.append(f"Sign traits:\n{sign_chunks[0].text}")
            _track_source(sign_chunks[0].metadata.get("source", ""))

        house_chunks = retrieval_query(house_name, entity_type="house", n_results=1)
        if house_chunks:
            parts.append(f"House domain:\n{house_chunks[0].text}")
            _track_source(house_chunks[0].metadata.get("source", ""))

        sections.append("\n\n".join(parts))

    return "<chart_context>\n" + header + "\n" + "\n\n".join(sections) + "\n</chart_context>"


_CLASSIFY_PROMPT = """You are a Vedic astrology classifier. Given a user message, determine:
1. Is this an astrology-related question? If not, return empty values for all fields.
2. If yes, identify the domain, relevant planets (1-3), and relevant houses (0-2).

Domain must be one of these exact values:
- "career" — work, job, profession, business, career direction
- "relationship" — love, marriage, compatibility, partnerships, family bonds
- "money" — finances, wealth, income, investments, financial security
- "health" — physical health, mental wellbeing, illness, vitality
- "non-astrology" — not an astrology question (casual chat, greetings, venting, small talk)

Only classify as astrology if the user is asking about one of these domains in a way that implies astrological guidance. Casual conversation, greetings, or emotional venting are NOT astrology questions — return "non-astrology" for domain."""


async def get_planet_and_house(user_message: str) -> AstroClassification:
    agent = Agent(
        name="AstroClassifier",
        instructions=_CLASSIFY_PROMPT,
        model="gpt-4o-mini",
        output_type=AstroClassification,
    )
    result = await Runner.run(agent, input=user_message)
    logger.debug("Classification: {c}", c=result.final_output)
    return result.final_output


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
    history = []
    for msg in messages:
        history.append({"role": msg.role, "content": msg.content})
    return history


async def generate_response(
    user_message: str,
    messages: list[Message],
    preferred_language: str = "en",
    birth_details: BirthDetails | None = None,
    chart: BirthChart | None = None,
) -> LLMResult:
    birth_details_section = _build_birth_details_section(birth_details)

    language_name = "Hindi" if preferred_language == "hi" else "English"
    system_prompt = SYSTEM_PROMPT.format(
        language_name=language_name,
        birth_details_section=birth_details_section,
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
