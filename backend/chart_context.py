from loguru import logger

from backend.retrieval import query as retrieval_query
from backend.schemas import AstroClassification, BirthChart, ResolvedPlanet

_retrieval_sources: list[str] = []


def track_source(source: str) -> None:
    if source and source not in _retrieval_sources:
        _retrieval_sources.append(source)


def pop_retrieval_sources() -> list[str]:
    """Return accumulated sources and clear the list."""
    sources = list(_retrieval_sources)
    _retrieval_sources.clear()
    return sources


_HOUSE_NAMES = [
    "First House", "Second House", "Third House", "Fourth House",
    "Fifth House", "Sixth House", "Seventh House", "Eighth House",
    "Ninth House", "Tenth House", "Eleventh House", "Twelfth House",
]


def house_number_to_name(house: int) -> str:
    return _HOUSE_NAMES[house - 1] if 1 <= house <= 12 else f"House {house}"


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
        house_name = house_number_to_name(rp.house)
        parts = [f"## {rp.planet} in {rp.sign} in the {house_name}"]

        planet_chunks = retrieval_query(rp.planet, entity_type="planet", n_results=1)
        if planet_chunks:
            parts.append(f"Planet meaning:\n{planet_chunks[0].text}")
            track_source(planet_chunks[0].metadata.get("source", ""))

        sign_chunks = retrieval_query(rp.sign, entity_type="sign", n_results=1)
        if sign_chunks:
            parts.append(f"Sign traits:\n{sign_chunks[0].text}")
            track_source(sign_chunks[0].metadata.get("source", ""))

        house_chunks = retrieval_query(house_name, entity_type="house", n_results=1)
        if house_chunks:
            parts.append(f"House domain:\n{house_chunks[0].text}")
            track_source(house_chunks[0].metadata.get("source", ""))

        sections.append("\n\n".join(parts))

    return "<chart_context>\n" + header + "\n" + "\n\n".join(sections) + "\n</chart_context>"
