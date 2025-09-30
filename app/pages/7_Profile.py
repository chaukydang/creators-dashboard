import pandas as pd
import streamlit as st

try:
    from app import utils as U
except ImportError:
    import utils as U

st.set_page_config(page_title="KOL Profile", page_icon="👤", layout="wide")

df = U.load_data()
cfg = U.load_config()
features = cfg.get("similarity", {}).get(
    "features", ["engagement_per_view", "engagement_per_1k_followers", "followers"]
)
k = int(cfg.get("similarity", {}).get("k", 10))

st.title("👤 KOL Profile")

# chọn KOL
name_col = "account" if "account" in df.columns else df.columns[0]
sel = st.selectbox("Chọn KOL", options=df[name_col].astype(str).unique())

d = df[df[name_col].astype(str) == str(sel)].copy()
if d.empty:
    st.warning("Không tìm thấy KOL.")
    st.stop()

idx = d.index[0]
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Thông tin tổng quan")
    fields = [
        "followers",
        "views_avg",
        "likes_avg",
        "comments_avg",
        "shares_avg",
        "engagement_per_view",
        "engagement_per_1k_followers",
        "kol_score",
        "country",
        "follower_tier",
        "title",
    ]
    rows = []
    for c in fields:
        if c in df.columns:
            val = df.loc[idx, c]
            if isinstance(val, int | float) and not pd.isna(val):
                rows.append(
                    (c, f"{val:,.4f}" if "engagement" in c or "kol_score" in c else f"{val:,.0f}")
                )
            else:
                rows.append((c, str(val)))
    st.table(pd.DataFrame(rows, columns=["Field", "Value"]))

with col2:
    st.subheader("Percentiles (context)")
    q = df[["engagement_per_view", "engagement_per_1k_followers", "followers"]].rank(pct=True)
    r = q.loc[idx].to_frame("percentile").reset_index().rename(columns={"index": "metric"})
    st.dataframe(r, use_container_width=True)

st.divider()
st.subheader("🔎 Similar creators")
sim = U.top_similar(df, idx=idx, features=features, k=k)
keep_cols = [
    name_col,
    "followers",
    "engagement_per_view",
    "engagement_per_1k_followers",
    "kol_score",
    "country",
    "follower_tier",
    "similarity",
]
keep_cols = [c for c in keep_cols if c in sim.columns]
st.dataframe(sim[keep_cols], use_container_width=True)

st.caption("Similarity dựa trên cosine của các feature đã cấu hình trong config.yaml")
