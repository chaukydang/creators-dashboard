import pandas as pd
import streamlit as st

from utils import load_data

st.title("Leaderboard")
df = load_data()

with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search account/title contains")
    chosen_tiers = st.multiselect("Follower tiers", sorted(df["follower_tier"].dropna().unique()))
    selected_countries = []
    if "country" in df.columns:
        countries = sorted([c for c in df["country"].dropna().unique()])
        selected_countries = st.multiselect("Country", countries)
    sort_metric = st.selectbox(
        "Sort by", ["kol_score", "engagement_per_view", "engagement_per_1k_followers", "followers"]
    )

mask = pd.Series(True, index=df.index)
if search:
    s = search.lower()
    cols = []
    if "account" in df.columns:
        cols.append("account")
    if "title" in df.columns:
        cols.append("title")
    if cols:
        mask &= (
            df[cols]
            .astype(str)
            .apply(lambda c: c.str.lower().str.contains(s, na=False))
            .any(axis=1)
        )
if chosen_tiers:
    mask &= df["follower_tier"].isin(chosen_tiers)
if "country" in df.columns and selected_countries:
    mask &= df["country"].isin(selected_countries)

dff = df[mask].copy().sort_values(sort_metric, ascending=False)
st.caption("Tip: Click column headers to sort; use top-right icon to export data.")
st.dataframe(dff.head(500), use_container_width=True)
