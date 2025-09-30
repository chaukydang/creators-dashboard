# app/pages/3_Country_Segments.py
import os
import sys

import matplotlib.pyplot as plt
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


st.title("Country & Segments")
df = U.load_data()

if "country" not in df.columns or df["country"].isna().all():
    st.warning("Dataset không có cột country.")
else:
    agg = (
        df.groupby("country", dropna=False)["kol_score"]
        .mean()
        .reset_index()
        .sort_values("kol_score", ascending=False)
    )
    st.subheader("Top Countries by Mean KOL Score")
    fig, ax = plt.subplots(figsize=(8, 6))
    top = agg.head(20)
    ax.barh(top["country"].astype(str), top["kol_score"])
    ax.invert_yaxis()
    ax.set_xlabel("Mean KOL Score (0-1)")
    st.pyplot(fig)

    st.subheader("Boxplot: EPV by Country (Top 10 by count)")
    top_countries = df["country"].value_counts().head(10).index.tolist()
    box_df = df[df["country"].isin(top_countries)]
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    data = [
        box_df.loc[box_df["country"] == c, "engagement_per_view"].dropna() for c in top_countries
    ]
    ax2.boxplot(data, tick_labels=[str(c) for c in top_countries], showfliers=False)
    ax2.set_ylabel("Engagement per View")
    st.pyplot(fig2)

st.subheader("Tier mix in a country")
if "country" in df.columns and df["country"].notna().any():
    opts = sorted([c for c in df["country"].dropna().unique()])
    selected = st.selectbox("Country", opts) if opts else None
    if selected:
        d = df[df["country"] == selected]
        mix = d["follower_tier"].value_counts().sort_index()
        fig3, ax3 = plt.subplots()
        mix.plot(kind="bar", ax=ax3)
        ax3.set_title(f"Follower tier mix — {selected}")
        ax3.set_ylabel("Count")
        st.pyplot(fig3)
