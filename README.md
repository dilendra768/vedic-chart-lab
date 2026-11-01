# Vedic Chart Lab ✦

A Python + Flask learning application that calculates sidereal planetary placements and selected Parashari divisional charts (Vargas) using Swiss Ephemeris.

## Features

- Sidereal planetary longitudes for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn and True Rahu; Ketu is calculated opposite Rahu.
- Lahiri, B.V. Raman and Krishnamurti ayanamsa options.
- Whole Sign, Equal, Placidus and Koch house-system options.
- Divisional chart selection: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45 and D60.
- Time-zone-aware local birth time conversion using Python's IANA `zoneinfo`.
- Responsive interface and transparent display of calculation settings.
- Unit tests for core sign and varga mapping helpers.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Birth data

Enter:
- Local birth date and clock time (not UTC).
- IANA time zone, e.g. `Asia/Kathmandu`, `Asia/Tokyo`.
- Latitude and longitude in decimal degrees.
- Ayanamsa, house system and divisional chart.

Use a reliable source for historical time-zone rules and birthplace coordinates. A birth time recorded inaccurately by even a few minutes can affect the Ascendant and divisional placements.

## Calculation conventions and limitations

This is a portfolio-grade educational implementation, not a certified astrology product.

- Planetary longitudes are computed by Swiss Ephemeris in sidereal mode.
- Lahiri is the default ayanamsa. Raman and Krishnamurti are also selectable.
- True Rahu is used; Ketu is exactly 180° opposite.
- In D1, the planet-house column is determined from the selected sidereal house cusps. In divisional charts, houses are shown by whole-sign counting from the varga Ascendant, a common display convention for this prototype.
- Varga rules are implemented as common Parashari mappings for the listed charts. There are differences between schools and software, especially for less frequently used Vargas. Verify against a trusted reference before relying on results.
- D30 uses the traditional unequal five-part scheme. D2 and several other vargas follow commonly used sign-start conventions.
- D60 is highly sensitive to birth-time accuracy: each division is only 30 arcminutes.
- This version does not calculate Vimshottari dasha, yogas, aspects, strength scores, or interpretive predictions.
- The demo does not store or transmit birth details to an external server. If deployed publicly, add HTTPS, privacy notices, abuse protection and an appropriate data-handling policy.

## Tests

```bash
pytest -q
```

## Suggested engineering roadmap

1. Add regression fixtures against a chosen reference ephemeris and document the reference settings.
2. Add chart-wheel SVG rendering with sign and house labels.
3. Add Vimshottari dasha calculation with unit tests.
4. Add JSON export and reproducible chart reports.
5. Add Docker, GitHub Actions CI and typed request validation.
6. Add location lookup only with a trusted geocoding provider and explicit user consent.

## Suggested GitHub repository description

`A Python + Flask Vedic astrology calculation workbench using Swiss Ephemeris: sidereal planetary positions, ayanamsa options and Parashari divisional charts.`

## License

MIT. Swiss Ephemeris is distributed under its own licensing terms. Review the Swiss Ephemeris license and choose the appropriate license (AGPL or a professional license) before distributing a product that depends on it. This repository's MIT license does not override dependency licenses.
