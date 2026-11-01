from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from flask import Flask, render_template, request
from chart_engine import calculate_chart, SIGNS, VARGAS

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html", signs=SIGNS, vargas=VARGAS, result=None, error=None)

@app.post("/calculate")
def calculate():
    form = {
        "name": request.form.get("name", "").strip()[:60],
        "birth_datetime": request.form.get("birth_datetime", "").strip(),
        "timezone": request.form.get("timezone", "Asia/Kathmandu").strip(),
        "latitude": request.form.get("latitude", "").strip(),
        "longitude": request.form.get("longitude", "").strip(),
        "ayanamsa": request.form.get("ayanamsa", "lahiri").strip().lower(),
        "house_system": request.form.get("house_system", "W").strip().upper(),
        "varga": request.form.get("varga", "1").strip(),
    }
    try:
        local_dt = datetime.fromisoformat(form["birth_datetime"])
        if local_dt.tzinfo is not None:
            raise ValueError("Enter local date and time without a UTC offset.")
        try:
            tz = ZoneInfo(form["timezone"])
        except ZoneInfoNotFoundError:
            raise ValueError("Unknown time zone. Use an IANA name such as Asia/Kathmandu.")
        # Reject ambiguous/nonexistent DST wall times rather than silently guessing.
        aware = local_dt.replace(tzinfo=tz, fold=0)
        round_trip = aware.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None)
        if round_trip != local_dt:
            raise ValueError("That local time may not exist because of a daylight-saving clock change.")
        lat = float(form["latitude"])
        lon = float(form["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitude must be -90 to 90 and longitude -180 to 180.")
        division = int(form["varga"])
        if division not in VARGAS:
            raise ValueError("Choose a supported divisional chart.")
        result = calculate_chart(
            local_dt=local_dt,
            tz=tz,
            latitude=lat,
            longitude=lon,
            ayanamsa=form["ayanamsa"],
            house_system=form["house_system"],
            division=division,
        )
        result["name"] = form["name"] or "Birth chart"
        result["birth_local"] = local_dt.strftime("%d %b %Y, %H:%M")
        result["timezone"] = form["timezone"]
        result["coordinates"] = f'{lat:.4f}, {lon:.4f}'
        return render_template("index.html", signs=SIGNS, vargas=VARGAS, result=result, error=None, form=form)
    except (ValueError, TypeError, KeyError) as exc:
        return render_template("index.html", signs=SIGNS, vargas=VARGAS, result=None, error=str(exc), form=form), 400
    except Exception as exc:
        app.logger.exception("Chart calculation failed")
        return render_template("index.html", signs=SIGNS, vargas=VARGAS, result=None,
                               error=f"Calculation failed: {exc}. Check the installation and input values.",
                               form=form), 500

if __name__ == "__main__":
    app.run(debug=True)
