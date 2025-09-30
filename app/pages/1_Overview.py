# app/pages/1_Overview.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from utils import kpi_fmt, load_data, number_fmt

st.title("Overview")
df = load_data()

with st.sidebar:
    st.header("Filters")
    countries = (
        sorted([c for c in df["country"].dropna().unique()]) if "country" in df.columns else []
    )
    selected_countries = st.multiselect(
        "Country", countries, default=countries[:10] if countries else []
    )
    min_f = int(df["followers"].min()) if "followers" in df.columns else 0
    max_f = int(df["followers"].max()) if "followers" in df.columns else 1_000_000
    min_followers = st.number_input("Min followers", value=max(0, min_f), step=1000)
    max_followers = st.number_input("Max followers", value=max_f, step=1000)

mask = pd.Series(True, index=df.index)
if "country" in df.columns and selected_countries:
    mask &= df["country"].isin(selected_countries)
if "followers" in df.columns:
    mask &= df["followers"].between(min_followers, max_followers)
dff = df[mask]

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("KOLs in view", number_fmt(len(dff)))
with c2:
    st.metric("Avg EPV", kpi_fmt(dff["engagement_per_view"].mean()))
with c3:
    st.metric("Median EPV", kpi_fmt(dff["engagement_per_view"].median()))
with c4:
    st.metric("Avg EP1k", kpi_fmt(dff["engagement_per_1k_followers"].mean()))
with c5:
    st.metric("Avg KOL Score", kpi_fmt(dff["kol_score"].mean()))

dff_sorted = dff.sort_values("followers", ascending=False)
cum = dff_sorted["followers"].fillna(0).cumsum()
total = dff_sorted["followers"].fillna(0).sum()

if total > 0 and len(dff_sorted) > 0:
    pct_creators = np.arange(1, len(dff_sorted) + 1) / len(dff_sorted) * 100
    pct_reach = (cum / total) * 100

    st.subheader("Pareto Reach (tập trung reach theo % KOL)")
    fig, ax = plt.subplots()
    ax.plot(pct_creators, pct_reach)
    ax.set_xlabel("% KOL (xếp hạng theo followers)")
    ax.set_ylabel("% Reach tích lũy")
    ax.set_title("Pareto reach")
    st.pyplot(fig)

    st.caption(
        "Nếu >70% reach nằm ở top 10–20% KOL → thị trường rất tập trung. Phối hợp Macro/Mega (awareness) + Micro/Mid (performance)."
    )

st.subheader("Distributions")
colA, colB = st.columns(2)
with colA:
    fig, ax = plt.subplots()
    dff["engagement_per_view"].dropna().hist(bins=40, ax=ax)
    ax.set_title("Engagement per View")
    st.pyplot(fig)
with colB:
    fig, ax = plt.subplots()
    dff["engagement_per_1k_followers"].dropna().hist(bins=40, ax=ax)
    ax.set_title("Engagement per 1k Followers")
    st.pyplot(fig)

st.subheader("Follower Tier Mix")
tier_counts = dff["follower_tier"].value_counts(dropna=False).sort_index()
fig3, ax3 = plt.subplots()
tier_counts.plot(kind="bar", ax=ax3)
ax3.set_title("KOL count by follower tier")
ax3.set_ylabel("Count")
st.pyplot(fig3)
