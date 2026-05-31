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
# Data by category
# -------------------------
migration_df = pd.DataFrame(
    [
        {"lat": 48.3794, "lon": 31.1656, "name": "Україна", "value": "Внутрішня міграція"},
        {"lat": 52.2297, "lon": 21.0122, "name": "Польща", "value": "Потік біженців"},
        {"lat": 52.5200, "lon": 13.4050, "name": "Німеччина", "value": "Релокація населення"},
    ]
)

cyber_df = pd.DataFrame(
    [
        {"lat": 37.7749, "lon": -122.4194, "name": "США", "value": "DDoS на провайдера"},
        {"lat": 50.4501, "lon": 30.5234, "name": "Україна", "value": "Фішингова кампанія"},
        {"lat": 51.5072, "lon": -0.1276, "name": "Велика Британія", "value": "Спроба зламу VPN"},
    ]
)

conflicts_df = pd.DataFrame(
    [
        {"lat": 31.7683, "lon": 35.2137, "name": "Близький Схід", "value": "Ескалація"},
        {"lat": 49.9935, "lon": 36.2304, "name": "Східна Європа", "value": "Локальні бої"},
        {"lat": 15.5007, "lon": 32.5599, "name": "Судан", "value": "Збройне протистояння"},
    ]
)

nat_df = pd.DataFrame(
    [
        {"lat": 35.6762, "lon": 139.6503, "name": "Японія", "value": "Сейсмічна активність"},
        {"lat": -33.8688, "lon": 151.2093, "name": "Австралія", "value": "Повені"},
        {"lat": -6.2088, "lon": 106.8456, "name": "Індонезія", "value": "Землетрус"},
    ]
)

log_df = pd.DataFrame(
    [
        {"lat": 25.2854, "lon": 51.5310, "name": "Катар", "value": "Газовий хаб"},
        {"lat": 51.9244, "lon": 4.4777, "name": "Роттердам", "value": "Портова логістика"},
        {"lat": 1.3521, "lon": 103.8198, "name": "Сінгапур", "value": "Морський вузол"},
    ]
)

cap_df = pd.DataFrame(
    [
        {"lat": 40.7128, "lon": -74.0060, "name": "Нью-Йорк", "value": "Волатильність ринку"},
        {"lat": 22.3193, "lon": 114.1694, "name": "Гонконг", "value": "Відтік капіталу"},
        {"lat": 47.3769, "lon": 8.5417, "name": "Цюрих", "value": "Захисні активи"},
    ]
)

res_df = pd.DataFrame(
    [
        {"lat": 24.7136, "lon": 46.6753, "name": "Саудівська Аравія", "value": "Нафта"},
        {"lat": 64.2008, "lon": -149.4937, "name": "Аляска", "value": "Енергоресурси"},
        {"lat": 61.5240, "lon": 105.3188, "name": "Сибір", "value": "Газ/метали"},
    ]
)

panic_df = pd.DataFrame(
    [
        {"lat": 41.9028, "lon": 12.4964, "name": "Італія", "value": "Зростання паніки"},
        {"lat": 48.8566, "lon": 2.3522, "name": "Франція", "value": "Інфошум"},
        {"lat": 40.4168, "lon": -3.7038, "name": "Іспанія", "value": "Соцмережевий сплеск"},
    ]
)

mil_df = pd.DataFrame(
    [
        {"lat": 46.4825, "lon": 30.7233, "name": "Чорне море", "value": "Активність БПЛА"},
        {"lat": 34.0522, "lon": -118.2437, "name": "Каліфорнія", "value": "Випробування ракет"},
        {"lat": 39.9042, "lon": 116.4074, "name": "Пекін", "value": "Аерокосмічний моніторинг"},
    ]
)

# -------------------------
# Sidebar
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

st.info("Система готова")


def make_scatter_layer(df: pd.DataFrame, color: list[int]) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color=color,
        get_radius=130000,
        pickable=True,
    )


# -------------------------
# Build layers dynamically (if/else)
# -------------------------
layers = []

if show_mig:
    layers.append(make_scatter_layer(migration_df, [52, 152, 219, 190]))
else:
    pass

if show_cyber:
    layers.append(make_scatter_layer(cyber_df, [220, 53, 69, 200]))
else:
    pass

if show_conf:
    layers.append(make_scatter_layer(conflicts_df, [255, 140, 0, 200]))
else:
    pass

if show_nat:
    layers.append(make_scatter_layer(nat_df, [46, 204, 113, 190]))
else:
    pass

if show_log:
    layers.append(make_scatter_layer(log_df, [155, 89, 182, 190]))
else:
    pass

if show_cap:
    layers.append(make_scatter_layer(cap_df, [241, 196, 15, 190]))
else:
    pass

if show_res:
    layers.append(make_scatter_layer(res_df, [26, 188, 156, 190]))
else:
    pass

if show_panic:
    layers.append(make_scatter_layer(panic_df, [231, 76, 60, 190]))
else:
    pass

if show_mil:
    layers.append(make_scatter_layer(mil_df, [127, 140, 141, 200]))
else:
    pass


# -------------------------
# Deck config (online-safe map background)
# -------------------------
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
    layers=layers,  # empty list => empty map
    tooltip={"text": "{name}\n{value}"},
)

# -------------------------
# Main layout
# -------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Інтерактивна стратегічна карта")
    st.pydeck_chart(deck, use_container_width=True)

    if len(layers) == 0:
        st.caption("Жоден шар не вибрано — карта порожня.")

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

if show_cyber:
    st.subheader("Останні дані про атаки")
    st.markdown(
        """
- DDoS-атака на регіональний дата-центр.
- Фішингова кампанія проти держустанов.
- Спроба доступу до VPN через компрометований акаунт.
"""
    )

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