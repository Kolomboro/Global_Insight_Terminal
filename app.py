import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Налаштування сторінки
st.set_page_config(layout="wide", page_title="Global Insight Terminal")
st.title("🌐 Global Insight Terminal | Strategic Dashboard")

# Пошуковий рядок
search_query = st.text_input("🔍 Пошук по об'єктах або подіях...", placeholder="Наприклад: Нафтобаза, Міст, ВВП...")

# Бічна панель
with st.sidebar:
    st.header("⚙️ Налаштування")
    with st.expander("🌍 Мова", expanded=False):
        st.radio("Оберіть мову", ["Українська", "English", "Polski"])
    
    with st.expander("📊 Шари даних", expanded=True):
        show_mig = st.checkbox("Міграція")
        show_cyber = st.checkbox("Кібератаки")
        show_conf = st.checkbox("Конфлікти")
        show_nat = st.checkbox("Катастрофи (Землетруси/Повені)")
        show_log = st.checkbox("Критична логістика")
        show_cap = st.checkbox("Відтік капіталу")
        show_res = st.checkbox("Ресурси (Геополітика)")
        show_panic = st.checkbox("Індекс паніки")
        show_mil = st.checkbox("Дрони / Ракети / Удари")

# Дані для карти
country_data = pd.DataFrame([
    {'lat': 48.3794, 'lon': 31.1656, 'country': 'Україна', 'pop': '41M', 'gdp': '200B USD', 'regime': 'Демократія', 'unemp': '15.4%', 'res': 'Агро, Метали, ІТ'},
    {'lat': 37.0902, 'lon': -95.7129, 'country': 'США', 'pop': '333M', 'gdp': '27T USD', 'regime': 'Федеративна Республіка', 'unemp': '4.1%', 'res': 'Нафта, Технології, Фінанси'},
    {'lat': 35.8617, 'lon': 104.1954, 'country': 'Китай', 'pop': '1.4B', 'gdp': '18T USD', 'regime': 'Комуністична партія', 'unemp': '5.2%', 'res': 'Виробництво, Рідкоземельні метали'},
    {'lat': 51.1657, 'lon': 10.4515, 'country': 'Німеччина', 'pop': '84M', 'gdp': '4.4T USD', 'regime': 'Парламентська республіка', 'unemp': '3.4%', 'res': 'Машинобудування, Хімія'},
    {'lat': 55.7558, 'lon': 37.6173, 'country': 'РФ', 'pop': '144M', 'gdp': '1.8T USD', 'regime': 'Авторитаризм', 'unemp': '3.0%', 'res': 'Нафта, Газ, Вугілля'},
])

# Визначення шару
layer = pdk.Layer(
    "ScatterplotLayer",
    country_data,
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=100000,
    pickable=True,
)

# Робоча область
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Інтерактивна стратегічна карта")
    view_state = pdk.ViewState(latitude=40, longitude=20, zoom=2, pitch=0)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Країна:</b> {country} <br/> <b>Режим:</b> {regime} <br/> <b>ВВП:</b> {gdp} <br/> <b>Ресурси:</b> {res}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    ))

with col2:
    if show_panic:
        st.subheader("🚨 Індекс паніки")
        st.progress(65)
    if show_mil:
        st.subheader("🎯 Військовий моніторинг")
        st.error("Зафіксовано активність")
    if show_cap:
        st.subheader("💰 Рух капіталу")
        st.line_chart(np.random.randn(10))

# Лог подій
st.divider()
st.subheader("📜 Оперативний лог подій")
event_data = pd.DataFrame({
    "Час": ["12:05", "11:30"],
    "Тип": ["🎯 Удар", "🚨 Паніка"],
    "Локація": ["Одеський порт", "Варшава"],
    "Деталі": ["Удар по хабу", "Чутки в мережі"]
})
st.table(event_data)