import streamlit as st

from utils import load_data

st.set_page_config(page_title="KOL Performance Dashboard", page_icon="📊", layout="wide")
st.title("📊 KOL Performance Tracking Dashboard")
st.caption(
    "Multi‑page dashboard for exploring KOL performance metrics. Use the sidebar to navigate pages."
)

df = load_data()
st.info(
    "Go to **Pages** on the left sidebar: Overview, Leaderboard, Country & Segments, Anomalies, and Export."
)
st.dataframe(df.head(20), use_container_width=True)
