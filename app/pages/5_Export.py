# app/pages/5_Export.py
import streamlit as st
from utils import load_data

st.title("Export")
df = load_data()
st.download_button("Download full dataset (CSV)", data=df.to_csv(index=False).encode("utf-8"),
                   file_name="kol_clean_export.csv", mime="text/csv")
