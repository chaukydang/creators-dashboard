
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(path: str = "kol_clean.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    for c in ["followers", "views_avg", "likes_avg", "comments_avg", "shares_avg",
              "engagement_per_view", "engagement_per_1k_followers", "kol_score"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    bins = [-1, 1e4, 1e5, 1e6, 1e7, np.inf]
    labels = ["Nano (<10k)", "Micro (10k-100k)", "Mid (100k-1M)", "Macro (1M-10M)", "Mega (10M+)"]
    if "followers" in df.columns:
        df["follower_tier"] = pd.cut(df["followers"], bins=bins, labels=labels)
    else:
        df["follower_tier"] = "Unknown"
    return df

def kpi_fmt(x, digits=4):
    if x is None or pd.isna(x): return "—"
    return f"{x:,.{digits}f}"

def number_fmt(x):
    if x is None or pd.isna(x): return "—"
    return f"{x:,.0f}"
