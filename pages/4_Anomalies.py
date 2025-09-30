import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from utils import load_data

st.title("Anomalies & Quality Checks")
df = load_data()

st.caption(
    "Simple heuristics: identify suspicious ratios or outliers. Tune thresholds to your business context."
)

if {"views_avg", "likes_avg"}.issubset(df.columns):
    df["like_view_ratio"] = df["likes_avg"] / df["views_avg"].replace(0, np.nan)
    q1, q3 = df["like_view_ratio"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    suspects = df[(df["like_view_ratio"] < lo) | (df["like_view_ratio"] > hi)]
    st.subheader("Outliers by Like/View Ratio")
    st.write(f"Thresholds: low<{lo:.4f}, high>{hi:.4f}")
    st.dataframe(
        suspects[
            [
                "account",
                "title",
                "followers",
                "views_avg",
                "likes_avg",
                "like_view_ratio",
                "kol_score",
            ]
        ].head(300),
        use_container_width=True,
    )

    st.subheader("Scatter: Followers vs EP1k (size = EPV)")
    d = df.dropna(subset=["followers", "engagement_per_1k_followers", "engagement_per_view"])[:2000]
    fig, ax = plt.subplots()
    sc = ax.scatter(
        d["followers"],
        d["engagement_per_1k_followers"],
        s=(d["engagement_per_view"] * 5000).clip(5, 200),
        alpha=0.6,
    )
    ax.set_xscale("log")
    ax.set_xlabel("Followers (log scale)")
    ax.set_ylabel("EP1k")
    st.pyplot(fig)
else:
    st.warning("Missing `views_avg` or `likes_avg`, cannot compute like/view anomalies.")
