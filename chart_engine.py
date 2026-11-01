"""Sidereal Vedic chart calculations using Swiss Ephemeris.

This project intentionally exposes its calculation conventions. Varga mappings
are common Parashari conventions; some lineages/software differ, especially
for less commonly used divisional charts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import swisseph as swe

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
VARGAS = {
    1: "D1 · Rashi", 2: "D2 · Hora", 3: "D3 · Drekkana", 4: "D4 · Chaturthamsa",
    7: "D7 · Saptamsa", 9: "D9 · Navamsa", 10: "D10 · Dasamsa",
    12: "D12 · Dwadasamsa", 16: "D16 · Shodasamsa", 20: "D20 · Vimsamsa",
    24: "D24 · Chaturvimsamsa", 27: "D27 · Saptavimsamsa",
    30: "D30 · Trimsamsa", 40: "D40 · Khavedamsa", 45: "D45 · Akshavedamsa",
    60: "D60 · Shashtiamsa"
}
PLANETS = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
    ("Rahu", swe.TRUE_NODE)
]
AYANAMSA = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "krishnamurti": swe.SIDM_KRISHNAMURTI}


def normalize(degrees: float) -> float:
    return degrees % 360.0


def sign_index(longitude: float) -> int:
    return int(normalize(longitude) // 30)


def degree_in_sign(longitude: float) -> float:
    return normalize(longitude) % 30.0


def _cyclic_varga_sign(base_sign: int, part: int, division: int, start_offset: int = 0) -> int:
    return (base_sign + start_offset + part) % 12


def divisional_sign(longitude: float, division: int) -> int:
    """Return sign index in a divisional chart (common Parashari mappings).

    D30 uses the traditional unequal 5-part scheme. For D2/D3/D4/D7/D9/D10/
    D12/D16/D20/D24/D27/D40/D45/D60, commonly taught sign-start rules are used.
    Other divisional charts use a clearly documented cyclic fallback.
    """
    if division == 1:
        return sign_index(longitude)

    base = sign_index(longitude)
    within = degree_in_sign(longitude)
    part = min(division - 1, int(within / (30.0 / division)))

    if division == 2:  # Hora: odd signs Leo/Cancer; even signs Cancer/Leo
        first = 4 if base % 2 == 0 else 3
        return (first + part) % 12
    if division == 3:  # sign, 5th, 9th
        return (base + part * 4) % 12
    if division == 4:
        return (base + part * 3) % 12
    if division == 7:
        start = base if base % 2 == 0 else (base + 6) % 12
        return (start + part) % 12
    if division == 9:  # movable same, fixed 9th, dual 5th
        modality_offset = [0, 8, 4][base % 3]
        return (base + modality_offset + part) % 12
    if division == 10:
        start = base if base % 2 == 0 else (base + 8) % 12
        return (start + part) % 12
    if division == 12:
        return (base + part) % 12
    if division == 16:
        modality_offset = [0, 4, 8][base % 3]
        return (base + modality_offset + part) % 12
    if division == 20:
        modality_offset = [0, 8, 4][base % 3]
        return (base + modality_offset + part) % 12
    if division == 24:
        start = 4 if base % 2 == 0 else 3
        return (start + part) % 12
    if division == 27:
        # Starts: Aries for fire, Cancer for earth, Libra for air, Capricorn for water.
        element_start = [0, 3, 6, 9][base % 4]
        return (element_start + part) % 12
    if division == 30:
        # Traditional unequal Trimsamsa divisions. Boundaries in degrees.
        # Odd signs: Aries 0-5, Aquarius 5-10, Sagittarius 10-18,
        # Gemini 18-25, Libra 25-30. Even signs: Taurus, Virgo,
        # Pisces, Capricorn, Scorpio with reversed boundaries.
        odd_segments = [(0, 5, 0), (5, 10, 10), (10, 18, 8), (18, 25, 2), (25, 30, 6)]
        even_segments = [(0, 5, 1), (5, 12, 5), (12, 20, 11), (20, 25, 9), (25, 30, 7)]
        segments = odd_segments if base % 2 == 0 else even_segments
        for low, high, target in segments:
            if low <= within < high:
                return target
        return segments[-1][2]
    if division == 40:
        start = 0 if base % 2 == 0 else 6
        return (start + part) % 12
    if division == 45:
        modality_offset = [0, 4, 8][base % 3]
        return (modality_offset + part) % 12
    if division == 60:
        start = 0 if base % 2 == 0 else 6
        return (start + part) % 12

    # Generic cyclic fallback for non-standard divisions; not a lineage-specific rule.
    return _cyclic_varga_sign(base, part, division)


def _planetary_position(jd_ut: float, planet_id: int) -> tuple[float, bool]:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    try:
        values, retflags = swe.calc_ut(jd_ut, planet_id, flags)
    except Exception:
        values, retflags = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL)
    return normalize(values[0]), values[3] < 0


def _house_from_cusps(longitude: float, cusps) -> int:
    """Find the house containing a longitude using the 12 sidereal cusps."""
    lon = normalize(longitude)
    cusp_values = [normalize(float(value)) for value in cusps[:12]]
    for index, start in enumerate(cusp_values):
        end = cusp_values[(index + 1) % 12]
        if start <= end:
            inside = start <= lon < end
        else:  # house interval crosses 0° Aries
            inside = lon >= start or lon < end
        if inside:
            return index + 1
    return 1


def _format_position(longitude: float, division: int) -> dict[str, Any]:
    idx = divisional_sign(longitude, division)
    deg = degree_in_sign(longitude)
    return {
        "sign": SIGNS[idx],
        "glyph": SIGN_GLYPHS[idx],
        "degree": deg,
        "degree_text": f"{int(deg):02d}° {int((deg % 1) * 60):02d}′"
    }


def calculate_chart(local_dt: datetime, tz, latitude: float, longitude: float,
                    ayanamsa: str = "lahiri", house_system: str = "W",
                    division: int = 1) -> dict[str, Any]:
    if ayanamsa not in AYANAMSA:
        raise ValueError("Unsupported ayanamsa.")
    if house_system not in {"W", "P", "E", "K"}:
        raise ValueError("Choose W (Whole Sign), P (Placidus), E (Equal) or K (Koch).")
    if division not in VARGAS:
        raise ValueError("Unsupported varga.")

    aware = local_dt.replace(tzinfo=tz)
    utc_dt = aware.astimezone(timezone.utc)
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)

    swe.set_sid_mode(AYANAMSA[ayanamsa])
    flags = swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system.encode("ascii"), flags)
    asc_lon = normalize(ascmc[0])
    mc_lon = normalize(ascmc[1])

    bodies = []
    for name, planet_id in PLANETS:
        lon, retrograde = _planetary_position(jd_ut, planet_id)
        pos = _format_position(lon, division)
        bodies.append({
            "name": name, "longitude": lon, "retrograde": retrograde,
            "sign": pos["sign"], "glyph": pos["glyph"], "degree": pos["degree_text"],
            "house": _house_from_cusps(lon, cusps) if division == 1 else None
        })

    # Ketu is always opposite the selected lunar node.
    rahu_lon = next(body["longitude"] for body in bodies if body["name"] == "Rahu")
    ketu_lon = normalize(rahu_lon + 180)
    ketu_pos = _format_position(ketu_lon, division)
    bodies.append({
        "name": "Ketu", "longitude": ketu_lon, "retrograde": True,
        "sign": ketu_pos["sign"], "glyph": ketu_pos["glyph"], "degree": ketu_pos["degree_text"],
        "house": _house_from_cusps(ketu_lon, cusps) if division == 1 else None
    })

    asc_pos = _format_position(asc_lon, division)
    mc_pos = _format_position(mc_lon, division)
    if division != 1:
        # For divisional charts, display houses by whole-sign counting from the varga Ascendant.
        asc_house_sign = divisional_sign(asc_lon, division)
        for body in bodies:
            body["house"] = ((SIGNS.index(body["sign"]) - asc_house_sign) % 12) + 1

    return {
        "division": division,
        "division_name": VARGAS[division],
        "ayanamsa": ayanamsa.title(),
        "ascendant": asc_pos,
        "mc": mc_pos,
        "julian_day_ut": jd_ut,
        "utc_datetime": utc_dt.strftime("%Y-%m-%d %H:%M UTC"),
        "planets": bodies,
        "disclaimer": "Traditional sidereal astrology calculation for learning and reflection. Interpretations are cultural, not scientifically established predictions."
    }
