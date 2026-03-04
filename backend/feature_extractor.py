from loguru import logger

from backend.schemas import BirthChart, ChartFeatures

# Standard Vedic astrology exaltation/debilitation signs
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra",
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries",
}

HOUSE_ORDINALS = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}


def _normalize(s: str) -> str:
    return s.lower().replace(" ", "_")


def extract_features(chart: BirthChart) -> ChartFeatures:
    features: list[str] = []

    for p in chart.planets:
        name = _normalize(p.planet)
        sign = _normalize(p.sign)
        ordinal = HOUSE_ORDINALS.get(p.house, f"{p.house}th")

        # Planet in house
        features.append(f"{name}_in_{ordinal}_house")

        # Planet in sign
        features.append(f"{name}_in_{sign}")

        # Planet strength
        if EXALTATION.get(p.planet) == p.sign:
            features.append(f"{name}_exalted")
        if DEBILITATION.get(p.planet) == p.sign:
            features.append(f"{name}_debilitated")

    # Planetary aspects (simplified: planets in same house or opposite houses)
    for i, p1 in enumerate(chart.planets):
        for p2 in chart.planets[i + 1:]:
            diff = abs(p1.house - p2.house)
            if diff == 0:
                features.append(f"{_normalize(p1.planet)}_conjunct_{_normalize(p2.planet)}")
            elif diff == 6:
                features.append(f"{_normalize(p1.planet)}_aspect_{_normalize(p2.planet)}")
            elif diff in (3, 9):  # Trine aspect (roughly)
                features.append(f"{_normalize(p1.planet)}_trine_{_normalize(p2.planet)}")
            elif diff in (4, 8):  # Square aspect
                features.append(f"{_normalize(p1.planet)}_square_{_normalize(p2.planet)}")

    logger.info("Extracted {n} features", n=len(features))
    return ChartFeatures(features=features)
