# app/App.py
# bootstrap trước
import os
import sys

import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# rồi import
try:
    from app import utils as U
except ModuleNotFoundError:
    import utils as U

st.set_page_config(page_title="KOL Performance Dashboard", page_icon="📊", layout="wide")
st.title("📊 KOL Performance Tracking Dashboard")
st.caption("Use the sidebar to navigate pages.")

df = U.load_data()  # chỉ kiểm tra nạp OK
st.dataframe(df.head(20), use_container_width=True)
st.info(
    "Đi tới mục **Pages** (sidebar) để xem Overview, Leaderboard, Country & Segments, Anomalies, Export."
)
