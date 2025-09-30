# app/pages/2_Leaderboard.py
import pandas as pd
import streamlit as st

try:
    from app import utils as U
except ImportError:
    import utils as U


st.title("Leaderboard")
df = U.load_data()

with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search account/title contains")
    tiers = st.multiselect("Follower tiers", sorted(df["follower_tier"].dropna().unique()))
    countries = (
        sorted([c for c in df["country"].dropna().unique()]) if "country" in df.columns else []
    )
    selected_countries = st.multiselect("Country", countries)
    sort_metric = st.selectbox(
        "Sort by", ["kol_score", "engagement_per_view", "engagement_per_1k_followers", "followers"]
    )

mask = pd.Series(True, index=df.index)
if search:
    s = search.lower()
    cols = [c for c in ["account", "title"] if c in df.columns]
    if cols:
        mask &= (
            df[cols]
            .astype(str)
            .apply(lambda c: c.str.lower().str.contains(s, na=False))
            .any(axis=1)
        )
if tiers:
    mask &= df["follower_tier"].isin(tiers)
if "country" in df.columns and selected_countries:
    mask &= df["country"].isin(selected_countries)

dff = df[mask].sort_values(sort_metric, ascending=False).head(500)
st.dataframe(dff, use_container_width=True)
