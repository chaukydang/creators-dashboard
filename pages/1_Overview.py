
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import load_data, kpi_fmt, number_fmt

st.title("Overview")
df = load_data()

with st.sidebar:
    st.header("Filters")
    selected_countries = []
    if "country" in df.columns:
        countries = sorted([c for c in df["country"].dropna().unique()])
        selected_countries = st.multiselect("Country", countries, default=countries[:10] if countries else [])
    min_followers = int(df["followers"].min()) if "followers" in df.columns else 0
    max_followers = int(df["followers"].max()) if "followers" in df.columns else 1_000_000
    min_followers = st.number_input("Min followers", value=max(0, min_followers), step=1000)
    max_followers = st.number_input("Max followers", value=max_followers, step=1000)

mask = pd.Series(True, index=df.index)
if "country" in df.columns and selected_countries:
    mask &= df["country"].isin(selected_countries)
if "followers" in df.columns:
    mask &= df["followers"].between(min_followers, max_followers)

dff = df[mask].copy()

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("KOLs in view", number_fmt(len(dff)))
with c2: st.metric("Avg EPV", kpi_fmt(dff["engagement_per_view"].mean()))
with c3: st.metric("Median EPV", kpi_fmt(dff["engagement_per_view"].median()))
with c4: st.metric("Avg EP1k", kpi_fmt(dff["engagement_per_1k_followers"].mean()))
with c5: st.metric("Avg KOL Score", kpi_fmt(dff["kol_score"].mean()))

st.subheader("Distributions")
colA, colB = st.columns(2)
with colA:
    fig1, ax1 = plt.subplots()
    dff["engagement_per_view"].dropna().hist(bins=40, ax=ax1)
    ax1.set_title("Engagement per View")
    st.pyplot(fig1)
with colB:
    fig2, ax2 = plt.subplots()
    dff["engagement_per_1k_followers"].dropna().hist(bins=40, ax=ax2)
    ax2.set_title("Engagement per 1k Followers")
    st.pyplot(fig2)

st.subheader("Follower Tier Mix")
tier_counts = dff["follower_tier"].value_counts(dropna=False).sort_index()
fig3, ax3 = plt.subplots()
tier_counts.plot(kind="bar", ax=ax3)
ax3.set_title("KOL count by follower tier"); ax3.set_ylabel("Count")
st.pyplot(fig3)
