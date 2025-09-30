# app/App.py
# --- ensure imports work both locally & on Streamlit Cloud ---

# --- ensure imports work both locally & on Streamlit Cloud ---
import os
import sys

import streamlit as st

from app.utils import load_data

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # repo root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# -------------------------------------------------------------


st.set_page_config(page_title="KOL Performance Dashboard", page_icon="📊", layout="wide")
st.title("📊 KOL Performance Tracking Dashboard")
st.caption("Use the sidebar to navigate pages.")

df = load_data()  # chỉ kiểm tra nạp OK
st.dataframe(df.head(20), use_container_width=True)
st.info(
    "Đi tới mục **Pages** (sidebar) để xem Overview, Leaderboard, Country & Segments, Anomalies, Export."
)
