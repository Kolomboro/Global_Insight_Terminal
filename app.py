import json
import re
from typing import List, Dict, Any

import pandas as pd
import pydeck as pdk
import streamlit as st
import google.generativeai as genai


# -------------------------
# Page setup
# -------------------------
st.set_page_config(page_title="Global Insight Terminal", layout="wide")
st.title("Global Insight Terminal")

search_query = st.text_input(
    "Пошук по об'єктах або подіях",
    placeholder="Наприклад: Нафтобаза, Міст, ВВП...",
)

# -------------------------
# Gemini integration
# -------------------------
def _extract_json(text: str) -> Any:
    """Extract JSON safely from raw model output."""
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        (text or "").strip(),
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()
    return json.loads(cleaned)


def fetch_migration_data_gemini(country: str) -> pd.DataFrame:
    """
    Query Gemini for migration data for a country (last year),
    return DataFrame with columns: lat, lon, count, name
    """
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Відсутній GEMINI_API_KEY у Streamlit secrets.")

    genai.configure(api_key=api_key)

# Автовибір першої доступної моделі з підтримкою generateContent
available_models = [
    m.name
    for m in genai.list_models()
    if "generateContent" in getattr(m, "supported_generation_methods", [])
]

selected_model = available_models[0] if available_models else "gemini-1.5-flash-latest"
model = genai.GenerativeModel(selected_model)

    prompt = f"""
Ти аналітик міграції. Поверни ТІЛЬКИ валідний JSON без пояснень.
Потрібні орієнтовні актуальні дані за останній рік для країни: "{country}".

Формат:
[
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<назва точки>"}},
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<назва точки>"}},
  {{"lat": <float>, "lon": <float>, "count": <int>, "name": "<назва точки>"}}
]
"""

    response = model.generate_content(prompt)
    parsed = _extract_json(response.text if response else "")

    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list) or not parsed:
        raise ValueError("Gemini повернув порожні або некоректні дані.")

    rows: List[Dict[str, Any]] = []
    for item in parsed:
        rows.append(
            {
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "count": int(item["count"]),
                "name": str(item["name"]),
            }
        )

    df = pd.DataFrame(rows, columns=["lat", "lon", "count", "name"])
    if df.empty:
        raise ValueError("Не вдалося сформувати набір даних міграції.")
    return df


# -------------------------
# Utility for map layers
# -------------------------
def make_layer(df: pd.DataFrame, color: List[int], radius: int = 120000) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color=color,
        get_radius=radius,
        pickable=True,
    )


def build_deck(layers: List[pdk.Layer]) -> pdk.Deck:
    return pdk.Deck(
        map_provider="carto",
        map_style=None,  # requested: guaranteed background behavior in your setup
        initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.3, pitch=0),
        layers=layers,
        tooltip={"html": "<b>{name}</b><br/>Значення: {count}"},
    )


# -------------------------
# Session state
# -------------------------
if "migration_df" not in st.session_state:
    st.session_state.migration_df = pd.DataFrame(columns=["lat", "lon", "count", "name"])

if "gemini_status" not in st.session_state:
    st.session_state.gemini_status = ""


# -------------------------
# Sidebar (always visible)
# -------------------------
with st.sidebar:
    st.header("Налаштування")

    with st.expander("Шари", expanded=True):
        show_mig = st.checkbox("Міграція", value=False)
        show_cyber = st.checkbox("Кібератаки", value=False)
        show_conf = st.checkbox("Конфлікти", value=False)
        show_nat = st.checkbox("Катастрофи (Землетруси/Повені)", value=False)
        show_log = st.checkbox("Критична логістика", value=False)
        show_cap = st.checkbox("Відтік капіталу", value=False)
        show_res = st.checkbox("Ресурси (Геополітика)", value=False)
        show_panic = st.checkbox("Індекс паніки", value=False)
        show_mil = st.checkbox("Дрони / Ракети / Удари", value=False)

    with st.expander("Налаштування мови", expanded=True):
        language = st.radio("Оберіть мову", ["Українська", "English", "Polski"])

    st.divider()
    country_for_ai = st.text_input("Країна для AI-аналізу міграції", value="Poland")
    refresh_clicked = st.button("Оновити дані", use_container_width=True)


# -------------------------
# Main status
# -------------------------
st.info("Система готова")

if refresh_clicked:
    try:
        st.session_state.migration_df = fetch_migration_data_gemini(country_for_ai)
        st.session_state.gemini_status = f"Дані Gemini оновлено для: {country_for_ai}"
    except Exception as exc:
        st.session_state.migration_df = pd.DataFrame(columns=["lat", "lon", "count", "name"])
        st.session_state.gemini_status = ""
        st.warning(f"Не вдалося отримати дані Gemini: {exc}")

if st.session_state.gemini_status:
    st.success(st.session_state.gemini_status)


# -------------------------
# Static data for other layers
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

nat_df = pd.DataFrame(
    [
        {"lat": 35.6762, "lon": 139.6503, "count": 18, "name": "Tokyo Seismic"},
        {"lat": -6.2088, "lon": 106.8456, "count": 22, "name": "Jakarta Flood Risk"},
    ]
)

log_df = pd.DataFrame(
    [
        {"lat": 51.9244, "lon": 4.4777, "count": 200, "name": "Rotterdam Port"},
        {"lat": 1.3521, "lon": 103.8198, "count": 250, "name": "Singapore Port"},
    ]
)

cap_df = pd.DataFrame(
    [
        {"lat": 40.7128, "lon": -74.0060, "count": 300, "name": "New York Outflow"},
        {"lat": 22.3193, "lon": 114.1694, "count": 280, "name": "Hong Kong Outflow"},
    ]
)

res_df = pd.DataFrame(
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

mil_df = pd.DataFrame(
    [
        {"lat": 46.4825, "lon": 30.7233, "count": 15, "name": "Black Sea Activity"},
        {"lat": 34.0522, "lon": -118.2437, "count": 9, "name": "LA Monitoring"},
    ]
)


# -------------------------
# Dynamic layers from checkboxes
# -------------------------
layers: List[pdk.Layer] = []

if show_mig:
    if st.session_state.migration_df.empty:
        st.warning("Шар 'Міграція' увімкнено, але дані ще не завантажено. Натисни 'Оновити дані'.")
    else:
        layers.append(make_layer(st.session_state.migration_df, [52, 152, 219, 190], radius=140000))

if show_cyber:
    layers.append(make_layer(cyber_df, [231, 76, 60, 185]))

if show_conf:
    layers.append(make_layer(conflicts_df, [243, 156, 18, 185]))

if show_nat:
    layers.append(make_layer(nat_df, [46, 204, 113, 185]))

if show_log:
    layers.append(make_layer(log_df, [155, 89, 182, 185]))

if show_cap:
    layers.append(make_layer(cap_df, [241, 196, 15, 185]))

if show_res:
    layers.append(make_layer(res_df, [26, 188, 156, 185]))

if show_panic:
    layers.append(make_layer(panic_df, [192, 57, 43, 185]))

if show_mil:
    layers.append(make_layer(mil_df, [127, 140, 141, 185]))


# -------------------------
# Main layout + map
# -------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Інтерактивна стратегічна карта")
    st.pydeck_chart(build_deck(layers), use_container_width=True)

with col2:
    if show_panic:
        st.subheader("Індекс паніки")
        st.progress(65)

    if show_mil:
        st.subheader("Військовий моніторинг")
        st.error("Зафіксовано активність")

    if show_cap:
        st.subheader("Рух капіталу")
        st.line_chart(pd.DataFrame({"value": [1, 3, 2, 5, 4, 6, 5]}))


# -------------------------
# Existing cyberattacks block (kept)
# -------------------------
if show_cyber:
    st.header("Останні дані про атаки")
    st.markdown(
        """
- DDoS-атака на регіональний дата-центр (підвищена мережна активність).
- Фішингова кампанія проти державних установ через підроблені email-домени.
- Спроба проникнення в корпоративну VPN-мережу через вразливий обліковий запис.
"""
    )