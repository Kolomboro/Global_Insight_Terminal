import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


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
# Sidebar
# -------------------------
with st.sidebar:
    st.header("Налаштування")

    with st.expander("Шари", expanded=True):
        show_mig = st.checkbox("Міграція")
        show_cyber = st.checkbox("Кібератаки")
        show_conf = st.checkbox("Конфлікти")
        show_nat = st.checkbox("Катастрофи (Землетруси/Повені)")
        show_log = st.checkbox("Критична логістика")
        show_cap = st.checkbox("Відтік капіталу")
        show_res = st.checkbox("Ресурси (Геополітика)")
        show_panic = st.checkbox("Індекс паніки")
        show_mil = st.checkbox("Дрони / Ракети / Удари")

    with st.expander("Налаштування мови", expanded=True):
        language = st.radio("Оберіть мову", ["Українська", "English", "Polski"])

st.info("Система готова")

# -------------------------
# Map data
# -------------------------
country_data = pd.DataFrame(
    [
        {
            "lat": 48.3794,
            "lon": 31.1656,
            "country": "Україна",
            "pop": "41M",
            "gdp": "200B USD",
            "regime": "Демократія",
            "unemp": "15.4%",
            "res": "Агро, Метали, ІТ",
        },
        {
            "lat": 37.0902,
            "lon": -95.7129,
            "country": "США",
            "pop": "333M",
            "gdp": "27T USD",
            "regime": "Федеративна Республіка",
            "unemp": "4.1%",
            "res": "Нафта, Технології, Фінанси",
        },
        {
            "lat": 35.8617,
            "lon": 104.1954,
            "country": "Китай",
            "pop": "1.4B",
            "gdp": "18T USD",
            "regime": "Комуністична партія",
            "unemp": "5.2%",
            "res": "Виробництво, Рідкоземельні метали",
        },
        {
            "lat": 51.1657,
            "lon": 10.4515,
            "country": "Німеччина",
            "pop": "84M",
            "gdp": "4.4T USD",
            "regime": "Парламентська республіка",
            "unemp": "3.4%",
            "res": "Машинобудування, Хімія",
        },
        {
            "lat": 55.7558,
            "lon": 37.6173,
            "country": "РФ",
            "pop": "144M",
            "gdp": "1.8T USD",
            "regime": "Авторитаризм",
            "unemp": "3.0%",
            "res": "Нафта, Газ, Вугілля",
        },
    ]
)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=country_data,
    get_position="[lon, lat]",
    get_color=[220, 60, 40, 180],
    get_radius=140000,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=20,
    longitude=0,
    zoom=1.4,
    pitch=0,
    bearing=0,
)

deck = pdk.Deck(
    map_provider="carto",
    map_style="light",
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip={
        "html": "<b>{country}</b><br/>Населення: {pop}<br/>ВВП: {gdp}<br/>Безробіття: {unemp}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    },
)

# -------------------------
# Main layout
# -------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Інтерактивна стратегічна карта")
    st.pydeck_chart(deck, use_container_width=True)

with col2:
    if show_panic:
        st.subheader("Індекс паніки")
        st.progress(65)

    if show_mil:
        st.subheader("Військовий моніторинг")
        st.error("Зафіксовано активність")

    if show_cap:
        st.subheader("Рух капіталу")
        st.line_chart(np.random.randn(10))

# -------------------------
# Optional block for cyberattacks layer
# -------------------------
if show_cyber:
    st.subheader("Останні дані про атаки")
    st.markdown(
        """
- DDoS-атака на регіональний дата-центр.
- Фішингова кампанія проти державних установ.
- Спроба доступу до VPN через компрометований акаунт.
"""
    )

# -------------------------
# Event log
# -------------------------
st.divider()
st.subheader("Оперативний лог подій")

event_data = pd.DataFrame(
    {
        "Час": ["12:05", "11:30"],
        "Тип": ["Удар", "Паніка"],
        "Локація": ["Одеський порт", "Варшава"],
        "Деталі": ["Удар по хабу", "Чутки в мережі"],
    }
)

st.table(event_data)