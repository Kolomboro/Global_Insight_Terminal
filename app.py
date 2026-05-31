import os
import json
import re
from datetime import date

import pandas as pd
import pydeck as pdk
import google.generativeai as genai


def fetch_migration_data_gemini(country: str, api_key: str) -> pd.DataFrame:
    """
    Повертає DataFrame у форматі для pydeck:
    columns: country, migrants_1y, lat, lon, source, year
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    current_year = date.today().year
    prompt = f"""
Ти аналітик міграції. Потрібні АКТУАЛЬНІ дані за останній рік для країни: {country}.
Поверни ТІЛЬКИ валідний JSON без пояснень:
{{
  "country": "назва країни",
  "migrants_1y": <ціле число>,
  "lat": <float>,
  "lon": <float>,
  "source": "посилання або назва джерела",
  "year": <рік>
}}
Використай максимально свіжі публічні дані, якщо доступні.
"""

    resp = model.generate_content(prompt)
    text = resp.text.strip()

    # Якщо модель обгорнула JSON у ```json ... ```
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL)

    data = json.loads(text)

    # Мінімальна валідація
    required = {"country", "migrants_1y", "lat", "lon", "source", "year"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Gemini response missing fields: {missing}")

    df = pd.DataFrame([{
        "country": data["country"],
        "migrants_1y": int(data["migrants_1y"]),
        "lat": float(data["lat"]),
        "lon": float(data["lon"]),
        "source": data["source"],
        "year": int(data.get("year", current_year)),
    }])
    return df


def build_deck_from_migration_df(df: pd.DataFrame) -> pdk.Deck:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=150000,
        get_fill_color=[220, 53, 69, 180],
        pickable=True,
    )

    # У pydeck правильний параметр — tooltip (не get_tooltip).
    # Але можна зробити helper-функцію:
    def get_tooltip():
        return {
            "html": "<b>{country}</b><br/>Мігрантів за рік: {migrants_1y}<br/>Джерело: {source}",
            "style": {"backgroundColor": "black", "color": "white"},
        }

    return pdk.Deck(
        map_provider="carto",
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=float(df["lat"].mean()),
            longitude=float(df["lon"].mean()),
            zoom=3,
            pitch=0,
        ),
        layers=[layer],
        tooltip=get_tooltip(),  # <- тут підказка при наведенні
    )