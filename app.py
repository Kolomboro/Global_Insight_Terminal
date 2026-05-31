import streamlit as st
import os

country = st.text_input("Країна", value="Poland")

# Ключ: спочатку з Streamlit secrets, fallback на env var
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if st.button("Оновити дані"):
    if not api_key:
        st.error("Немає GEMINI_API_KEY у secrets або env.")
    else:
        df = fetch_migration_data_gemini(country, api_key)
        st.dataframe(df)
        st.pydeck_chart(build_deck_from_migration_df(df), use_container_width=True)