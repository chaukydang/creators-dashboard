# app/pages/4_Anomalies.py
import streamlit as st, pandas as pd, numpy as np, matplotlib.pyplot as plt
from utils import load_data

st.title("Anomalies & Quality Checks")
df = load_data()
st.caption("Heuristics: Like/View, Comment/View, Share/View — phát hiện outliers (IQR).")

def iqr_bounds(s: pd.Series):
    q1, q3 = s.quantile([0.25,0.75]); iqr = q3-q1
    return q1-1.5*iqr, q3+1.5*iqr

for ratio in ["like_view_ratio","comment_view_ratio","share_view_ratio"]:
    if ratio in df.columns and df[ratio].notna().sum()>0:
        lo, hi = iqr_bounds(df[ratio].dropna())
        suspects = df[(df[ratio] < lo) | (df[ratio] > hi)]
        st.subheader(f"Outliers by {ratio} (±1.5 IQR) — showing up to 300 rows")
        cols = [c for c in ["account","title","followers","views_avg","likes_avg","comments_avg","shares_avg",ratio,"engagement_per_view","engagement_per_1k_followers","kol_score"] if c in df.columns]
        st.dataframe(suspects[cols].head(300), use_container_width=True)

if {"followers","engagement_per_1k_followers","engagement_per_view"}.issubset(df.columns):
    st.subheader("Scatter: Followers vs EP1k (size = EPV)")
    d = df.dropna(subset=["followers","engagement_per_1k_followers","engagement_per_view"]).copy()
    d = d.sample(min(2000, len(d)), random_state=42)
    fig, ax = plt.subplots()
    sc = ax.scatter(d["followers"], d["engagement_per_1k_followers"],
                    s=(d["engagement_per_view"]*5000).clip(5,200), alpha=0.6)
    ax.set_xscale("log"); ax.set_xlabel("Followers (log)"); ax.set_ylabel("EP1k"); st.pyplot(fig)
