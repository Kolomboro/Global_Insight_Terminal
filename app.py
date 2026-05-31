import json
import re
from typing import List

import pandas as pd
import pydeck as pdk
import streamlit as st
import google.generativeai as genai


# -------------------------
# Page config + title (залишаємо)
# -------------------------
st.set_page_config(page_title="Global Insight Terminal", layout="wide")
st.title("Global Insight Terminal")


# -------------------------
# Gemini functions
# -------------------------
def fetch_migration_data_gemini(country: str, api_key: str) -> pd.DataFrame:
    """
    Отримує актуальні (наскільки можливо) дані про міграцію через Gemini
    і повертає DataFrame з колонками:
    lat, lon, count, name
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
Ти аналітик міграції.
Поверни ТІЛЬКИ валідний JSON масив без пояснень, markdown і зайвого тексту.
Потрібні оцінки/факти за останній рік для країни "{country}".
Формат:
[
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<місто/регіон>"}},
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<місто/регіон>"}},
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<місто/регіон>"}}
]
Якщо точних цифр немає, поверни найбільш обґрунтовані публічні оцінки.
"""

    response = model.generate_content(prompt)
    raw_text = (response.text or "").strip()

    # прибираємо ```json ... ```
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        raw_text,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()

    data = json.loads(cleaned)

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Gemini повернув порожню або неочікувану структуру даних.")

    normalized = []
    for row in data:
        normalized.append(
            {
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "count": int(row["count"]),
                "name": str(row["name"]),
            }
        )

    return pd.DataFrame(normalized, columns=["lat", "lon", "count", "name"])


def build_deck_from_migration_df(df: pd.DataFrame) -> pdk.Deck:
    """
    Перетворює DataFrame (lat, lon, count, name) у pdk.Deck.
    """
    if df.empty:
        return pdk.Deck(
            map_provider="carto",
            map_style="light",
            initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.3, pitch=0),
            layers=[],
            tooltip={"text": "{name}\nМігрантів: {count}"},
        )

    migration_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius="max(50000, count * 0.03)",
        get_fill_color=[52, 152, 219, 180],
        pickable=True,
    )

    return pdk.Deck(
        map_provider="carto",
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=float(df["lat"].mean()),
            longitude=float(df["lon"].mean()),
            zoom=3,
            pitch=0,
        ),
        layers=[migration_layer],
        tooltip={"html": "<b>{name}</b><br/>Мігрантів: {count}"},
    )


# -------------------------
# Helper for non-migration layers
# -------------------------
def make_layer(df: pd.DataFrame, color: List[int], radius: int = 120000) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=radius,
        get_fill_color=color,
        pickable=True,
    )


# -------------------------
# Sidebar UI (залишаємо + розширюємо)
# -------------------------
with st.sidebar:
    with st.expander("Шари", expanded=True):
        migration = st.checkbox("Міграція")
        cyberattacks = st.checkbox("Кібератаки")
        conflicts = st.checkbox("Конфлікти")
        disasters = st.checkbox("Катастрофи (Землетруси/Повені)")
        logistics = st.checkbox("Критична логістика")
        capital = st.checkbox("Відтік капіталу")
        resources = st.checkbox("Ресурси (Геополітика)")
        panic = st.checkbox("Індекс паніки")
        military = st.checkbox("Дрони / Ракети / Удари")

    with st.expander("Налаштування мови", expanded=True):
        language = st.radio("Оберіть мову", ["Українська", "English", "Polski"])

    st.divider()
    country = st.text_input("Країна для міграції", value="Poland")
    refresh_data = st.button("Оновити дані", use_container_width=True)


# -------------------------
# Status info (залишаємо)
# -------------------------
st.info("Система готова")


# -------------------------
# Static datasets for other categories
# -------------------------
cyber_df = pd.DataFrame(
    [
        {"lat": 50.4501, "lon": 30.5234, "count": 1200, "name": "Kyiv Cyber Events"},
        {"lat": 51.5072, "lon": -0.1276, "count": 900, "name": "London Incidents"},
        {"lat": 38.9072, "lon": -77.0369, "count": 1100, "name": "Washington Alerts"},
    ]
)

conflicts_df = pd.DataFrame(
    [
        {"lat": 49.9935, "lon": 36.2304, "count": 75, "name": "Kharkiv Region"},
        {"lat": 31.7683, "lon": 35.2137, "count": 62, "name": "Jerusalem Area"},
        {"lat": 33.3152, "lon": 44.3661, "count": 41, "name": "Baghdad Zone"},
    ]
)

disasters_df = pd.DataFrame(
    [
        {"lat": 35.6762, "lon": 139.6503, "count": 18, "name": "Tokyo Seismic"},
        {"lat": -6.2088, "lon": 106.8456, "count": 22, "name": "Jakarta Flood Risk"},
    ]
)

logistics_df = pd.DataFrame(
    [
        {"lat": 51.9244, "lon": 4.4777, "count": 200, "name": "Rotterdam Port"},
        {"lat": 1.3521, "lon": 103.8198, "count": 250, "name": "Singapore Port"},
    ]
)

capital_df = pd.DataFrame(
    [
        {"lat": 40.7128, "lon": -74.0060, "count": 300, "name": "New York Outflow"},
        {"lat": 22.3193, "lon": 114.1694, "count": 280, "name": "Hong Kong Outflow"},
    ]
)

resources_df = pd.DataFrame(
    [
        {"lat": 24.7136, "lon": 46.6753, "count": 500, "name": "Riyadh Oil"},
        {"lat": 61.5240, "lon": 105.3188, "count": 420, "name": "Siberia Gas"},
    ]
)

panic_df = pd.DataFrame(
    [
        {"lat": 48.8566, "lon": 2.3522, "count": 67, "name": "Paris Panic Index"},
        {"lat": 41.9028, "lon": 12.4964, "count": 59, "name": "Rome Panic Index"},
    ]
)

military_df = pd.DataFrame(
    [
        {"lat": 46.4825, "lon": 30.7233, "count": 15, "name": "Black Sea Activity"},
        {"lat": 34.0522, "lon": -118.2437, "count": 9, "name": "LA Monitoring"},
    ]
)


# -------------------------
# Migration data state + Gemini call
# -------------------------
if "migration_df" not in st.session_state:
    st.session_state.migration_df = pd.DataFrame(columns=["lat", "lon", "count", "name"])

if refresh_data:
    try:
        # Безпечний варіант: ключ тільки із secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        st.session_state.migration_df = fetch_migration_data_gemini(country, api_key)
        st.success(f"Дані для '{country}' оновлено через Gemini.")
    except KeyError:
        st.error("Не знайдено GEMINI_API_KEY у Streamlit secrets.")
    except Exception as e:
        st.error(f"Помилка запиту до Gemini: {e}")


# -------------------------
# Dynamic map layers by checkboxes
# -------------------------
layers = []

if migration and not st.session_state.migration_df.empty:
    layers.append(
        make_layer(st.session_state.migration_df, [52, 152, 219, 190], radius=140000)
    )

if cyberattacks:
    layers.append(make_layer(cyber_df, [231, 76, 60, 185]))

if conflicts:
    layers.append(make_layer(conflicts_df, [243, 156, 18, 185]))

if disasters:
    layers.append(make_layer(disasters_df, [46, 204, 113, 185]))

if logistics:
    layers.append(make_layer(logistics_df, [155, 89, 182, 185]))

if capital:
    layers.append(make_layer(capital_df, [241, 196, 15, 185]))

if resources:
    layers.append(make_layer(resources_df, [26, 188, 156, 185]))

if panic:
    layers.append(make_layer(panic_df, [192, 57, 43, 185]))

if military:
    layers.append(make_layer(military_df, [127, 140, 141, 185]))


deck = pdk.Deck(
    map_provider="carto",
    map_style="light",
    initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.3, pitch=0),
    layers=layers,  # якщо список порожній -> порожня карта
    tooltip={"html": "<b>{name}</b><br/>Значення: {count}"},
)

st.subheader("Інтерактивна стратегічна карта")
st.pydeck_chart(deck, use_container_width=True)


# -------------------------
# Existing cyberattacks content (залишаємо)
# -------------------------
if cyberattacks:
    st.header("Останні дані про атаки")
    st.markdown(
        """
- DDoS-атака на регіональний дата-центр (підвищена мережна активність).
- Фішингова кампанія проти державних установ через підроблені email-домени.
- Спроба проникнення в корпоративну VPN-мережу через вразливий обліковий запис.
"""
    )