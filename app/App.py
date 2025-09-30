# --- bootstrap: make sure Python sees the repo root ---
import os
import sys

import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # repo root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ------------------------------------------------------

# Prefer app.utils; if missing attributes, fallback to top-level utils
try:
    from app import utils as U  # noqa: E402
except ModuleNotFoundError:  # noqa: E402
    import utils as U  # noqa: E402

# Guard: if critical functions not found in app.utils, fallback to root utils
if not all(hasattr(U, name) for name in ("load_data", "kpi_fmt", "number_fmt")):
    try:
        import utils as U  # noqa: E402
    except Exception:
        pass

st.set_page_config(page_title="KOL Performance Dashboard", page_icon="📊", layout="wide")

st.title("📊 KOL Performance Tracking Dashboard")
st.caption("Use the sidebar to navigate pages.")

df = U.load_data()  # chỉ kiểm tra nạp OK
st.dataframe(df.head(20), use_container_width=True)
st.info(
    "Đi tới mục **Pages** (sidebar) để xem Overview, Leaderboard, Country & Segments, Anomalies, Export."
)
