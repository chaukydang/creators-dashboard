# app/pages/5_Export.py
import streamlit as st

try:
    from app import utils as U
except ImportError:
    import utils as U

st.title("Export")
df = U.load_data()
st.download_button(
    "Download full dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="kol_clean_export.csv",
    mime="text/csv",
)
