# app/pages/5_Export.py
import os
import sys

import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from app import utils as U  # noqa: E402
except ModuleNotFoundError:  # noqa: E402
    import utils as U  # noqa: E402

# Guard: nếu thiếu attr (ví dụ number_fmt), fallback sang root utils
if not all(hasattr(U, name) for name in ("kpi_fmt", "number_fmt", "load_data")):
    try:
        import utils as U  # noqa: E402
    except Exception:
        pass

st.title("Export")
df = U.load_data()
st.download_button(
    "Download full dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="kol_clean_export.csv",
    mime="text/csv",
)
