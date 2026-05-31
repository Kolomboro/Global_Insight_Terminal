import streamlit as st

st.set_page_config(page_title="Global Insight Terminal", layout="wide")

st.title("Global Insight Terminal")

with st.sidebar:
    with st.expander("Шари", expanded=True):
        migration = st.checkbox("Міграція")
        cyberattacks = st.checkbox("Кібератаки")
        conflicts = st.checkbox("Конфлікти")

    with st.expander("Налаштування мови", expanded=True):
        language = st.radio("Оберіть мову", ["Українська", "English", "Polski"])

st.info("Система готова")
if cyberattacks:
    st.header("Останні дані про атаки")
    st.markdown(
        """
        - DDoS-атака на регіональний дата-центр (підвищена мережна активність).
        - Фішингова кампанія проти державних установ через підроблені email-домени.
        - Спроба проникнення в корпоративну VPN-мережу через вразливий обліковий запис.
        """
    )