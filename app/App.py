# app/App.py
import streamlit as st

from utils import load_data

st.set_page_config(page_title="KOL Performance Dashboard", page_icon="📊", layout="wide")
st.title("📊 KOL Performance Tracking Dashboard")
st.caption("Use the sidebar to navigate pages.")

df = load_data()  # chỉ kiểm tra nạp OK
st.dataframe(df.head(20), use_container_width=True)
st.info(
    "Đi tới mục **Pages** (sidebar) để xem Overview, Leaderboard, Country & Segments, Anomalies, Export."
)
