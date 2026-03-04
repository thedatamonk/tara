from geopy.geocoders import Nominatim
from kerykeion import AstrologicalSubject, AstrologicalSubjectFactory, ChartDataFactory, ChartDrawer
from loguru import logger
from timezonefinder import TimezoneFinder

from backend.schemas import BirthChart, BirthDetails, PlanetPlacement

SIGN_FULL_NAMES = {
    "Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Can": "Cancer",
    "Leo": "Leo", "Vir": "Virgo", "Lib": "Libra", "Sco": "Scorpio",
    "Sag": "Sagittarius", "Cap": "Capricorn", "Aqu": "Aquarius", "Pis": "Pisces",
}

HOUSE_MAP = {
    "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
    "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
    "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

PLANET_ATTRS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "true_north_lunar_node",
]

HOUSE_ATTRS = [
    "first_house", "second_house", "third_house", "fourth_house",
    "fifth_house", "sixth_house", "seventh_house", "eighth_house",
    "ninth_house", "tenth_house", "eleventh_house", "twelfth_house",
]

_geocoder = Nominatim(user_agent="tara")
_tz_finder = TimezoneFinder()


def _full_sign(abbrev: str) -> str:
    return SIGN_FULL_NAMES.get(abbrev, abbrev)


def _geocode(place: str) -> tuple[float, float, str]:
    """Geocode a place name to (lat, lng, timezone)."""
    location = _geocoder.geocode(place)
    if not location:
        raise ValueError(f"Could not geocode location: {place}")
    lat, lng = location.latitude, location.longitude
    tz = _tz_finder.timezone_at(lat=lat, lng=lng)
    if not tz:
        raise ValueError(f"Could not determine timezone for: {place}")
    logger.info("Geocoded {place} → lat={lat}, lng={lng}, tz={tz}",
                place=place, lat=lat, lng=lng, tz=tz)
    return lat, lng, tz


def generate_chart(details: BirthDetails) -> BirthChart:
    year, month, day = (int(x) for x in details.birth_date.split("-"))
    hour, minute = (int(x) for x in details.birth_time.split(":"))

    logger.info(
        "Generating chart for {name} born {date} {time} at {place}",
        name=details.name, date=details.birth_date,
        time=details.birth_time, place=details.birth_place,
    )

    # Geocode the birth place to get lat/lng/tz
    if details.latitude is not None and details.longitude is not None:
        lat, lng = details.latitude, details.longitude
        tz_str = _tz_finder.timezone_at(lat=lat, lng=lng) or "UTC"
    else:
        lat, lng, tz_str = _geocode(details.birth_place)

    subject = AstrologicalSubject(
        name=details.name, year=year, month=month, day=day,
        hour=hour, minute=minute, city=details.birth_place,
        lat=lat, lng=lng, tz_str=tz_str,
    )

    planets = []
    for attr in PLANET_ATTRS:
        p = getattr(subject, attr)
        name = p.name.replace("_", " ")
        if "Lunar_Node" in p.name or "Lunar Node" in name:
            name = "Rahu"
        planets.append(PlanetPlacement(
            planet=name,
            sign=_full_sign(p.sign),
            house=HOUSE_MAP.get(p.house, 1),
            degree=round(p.position, 2),
        ))

    # Add Ketu (opposite of Rahu)
    rahu = planets[-1]
    ketu_house = ((rahu.house - 1 + 6) % 12) + 1
    ketu_sign_idx = (list(SIGN_FULL_NAMES.values()).index(rahu.sign) + 6) % 12
    ketu_sign = list(SIGN_FULL_NAMES.values())[ketu_sign_idx]
    planets.append(PlanetPlacement(
        planet="Ketu", sign=ketu_sign, house=ketu_house,
        degree=round(rahu.degree, 2),
    ))

    ascendant_point = subject.first_house
    ascendant = _full_sign(ascendant_point.sign)

    houses = {}
    for i, attr in enumerate(HOUSE_ATTRS, 1):
        h = getattr(subject, attr)
        houses[i] = _full_sign(h.sign)

    logger.info("Chart generated: ascendant={asc}", asc=ascendant)
    return BirthChart(planets=planets, ascendant=ascendant, houses=houses)


def generate_chart_svg(details: BirthDetails) -> str:
    """Generate a natal chart SVG string using Kerykeion's chart drawer."""
    year, month, day = (int(x) for x in details.birth_date.split("-"))
    hour, minute = (int(x) for x in details.birth_time.split(":"))

    if details.latitude is not None and details.longitude is not None:
        lat, lng = details.latitude, details.longitude
        tz_str = _tz_finder.timezone_at(lat=lat, lng=lng) or "UTC"
    else:
        lat, lng, tz_str = _geocode(details.birth_place)

    subject = AstrologicalSubjectFactory.from_birth_data(
        name=details.name, year=year, month=month, day=day,
        hour=hour, minute=minute, city=details.birth_place,
        lat=lat, lng=lng, tz_str=tz_str,
    )

    chart_data = ChartDataFactory.create_natal_chart_data(subject)
    drawer = ChartDrawer(chart_data=chart_data, theme="dark")
    svg_string = drawer.generate_svg_string()

    logger.info("SVG chart generated for {name}", name=details.name)
    return svg_string
