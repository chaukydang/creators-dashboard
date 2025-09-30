# pages/6_Insights.py
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

st.title("Insights (Auto)")

df = U.load_data()

# ----- 0) Guard: cột cần thiết
need = {"followers", "engagement_per_view", "engagement_per_1k_followers", "kol_score"}
if not need.issubset(df.columns):
    st.error(f"Thiếu cột bắt buộc: {need - set(df.columns)}")
    st.stop()

# ----- 1) Insight cards (toàn cục)
N = len(df)
top10p = max(1, int(0.10 * N))
top20p = max(1, int(0.20 * N))

df_sorted_f = df.sort_values("followers", ascending=False)
reach_total = df["followers"].fillna(0).sum()
reach_top10p = df_sorted_f.head(top10p)["followers"].fillna(0).sum()
reach_top20p = df_sorted_f.head(top20p)["followers"].fillna(0).sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("KOLs", U.number_fmt(N))
with c2:
    st.metric("Top 10% giữ % Reach", U.kpi_fmt(100 * reach_top10p / max(reach_total, 1e-9), 2))
with c3:
    st.metric("Top 20% giữ % Reach", U.kpi_fmt(100 * reach_top20p / max(reach_total, 1e-9), 2))
with c4:
    st.metric("Median EPV", U.kpi_fmt(df["engagement_per_view"].median()))
with c5:
    st.metric("Median EP1k", U.kpi_fmt(df["engagement_per_1k_followers"].median()))

st.caption(
    "Insight: nếu >70% tổng follower nằm ở top 10–20% KOL → thị trường rất tập trung; chiến lược cần phối hợp Macro/Mega cho awareness + Micro/Mid cho performance."
)

# ----- 2) Lorenz & Pareto (reach concentration)
st.subheader("Reach concentration (Lorenz & Pareto view)")
x = df_sorted_f["followers"].fillna(0).to_numpy()
if x.sum() > 0:
    share = x / x.sum()
    cum_share = np.cumsum(np.sort(share))  # Lorenz dùng sort tăng dần
    pts = np.linspace(0, 1, len(cum_share), endpoint=True)
    # Gini ~ 1 - 2 * area under Lorenz
    gini = 1 - 2 * np.trapezoid(cum_share, pts)

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], linestyle="--", label="Equality line")
    ax.plot(pts, cum_share, label=f"Lorenz curve (Gini≈{gini:.2f})")
    ax.set_xlabel("Tỷ lệ KOL (tích lũy)")
    ax.set_ylabel("Tỷ lệ Reach (tích lũy)")
    ax.legend()
    st.pyplot(fig)

    st.caption(
        "Gini cao → reach tập trung vào ít KOL. Gợi ý: phân bổ ngân sách tránh phụ thuộc vài ‘siêu sao’."
    )
else:
    st.info("Followers tổng = 0, bỏ qua Lorenz.")

# ----- 3) Decile table (phân vị theo followers & chất lượng)
st.subheader("Decile by Followers (so sánh chất lượng theo quy mô)")
df_dec = df.copy()
df_dec["followers_decile"] = (
    pd.qcut(df_dec["followers"].rank(method="first"), 10, labels=[f"D{i}" for i in range(1, 11)])
    if df["followers"].notna().sum() >= 10
    else "All"
)

grp = (
    df_dec.groupby("followers_decile", observed=False)
    .agg(
        kol_count=("followers", "count"),
        followers_sum=("followers", "sum"),
        epv_med=("engagement_per_view", "median"),
        ep1k_med=("engagement_per_1k_followers", "median"),
        kol_med=("kol_score", "median"),
    )
    .reset_index()
)

st.dataframe(grp, use_container_width=True)
st.caption(
    "Insight: decile đầu (D10: to nhất) thường có median EP1k thấp hơn; decile giữa (D4-D7) hay là ‘điểm ngọt’ cho performance."
)

# ----- 4) Benchmark theo follower tier & country
st.subheader("Benchmark theo Follower Tier")
if "follower_tier" in df.columns:
    bench_tier = (
        df.groupby("follower_tier", observed=False)
        .agg(
            n=("follower_tier", "count"),
            epv_med=("engagement_per_view", "median"),
            ep1k_med=("engagement_per_1k_followers", "median"),
            kol_med=("kol_score", "median"),
        )
        .reset_index()
        .sort_values("ep1k_med", ascending=False)
    )

    st.dataframe(bench_tier, use_container_width=True)
    st.caption("Insight: Micro/Mid thường dẫn đầu về EPV/EP1k → phù hợp KPI conversion/CPA.")

st.subheader("Benchmark theo Country (nếu có)")
if "country" in df.columns and df["country"].notna().any():
    bench_cty = (
        df.groupby("country")[["engagement_per_view", "engagement_per_1k_followers", "kol_score"]]
        .median()
        .sort_values("kol_score", ascending=False)
        .round(4)
    )
    st.dataframe(bench_cty.head(25), use_container_width=True)
    st.caption("Tip: dùng median thay mean để đỡ nhiễu bởi outliers; lọc country có n nhỏ.")


# ----- 5) Outlier & Quality Flags (robust) -----
def add_ratio(df, num_col, den_col, out_col):
    if num_col in df.columns and den_col in df.columns:
        df[out_col] = df[num_col] / df[den_col].replace(0, np.nan)


# Tạo các ratio nếu có đủ cột
add_ratio(df, "likes_avg", "views_avg", "like_view_ratio")
add_ratio(df, "comments_avg", "views_avg", "comment_view_ratio")
add_ratio(df, "shares_avg", "views_avg", "share_view_ratio")


def iqr_bounds(s: pd.Series):
    s = s.dropna()
    if s.empty:
        return None, None
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


flags = []

for ratio_col in ["like_view_ratio", "comment_view_ratio", "share_view_ratio"]:
    if ratio_col in df.columns and df[ratio_col].notna().sum() > 0:
        lo, hi = iqr_bounds(df[ratio_col])
        if lo is not None:
            low_out = df[df[ratio_col] < lo]
            high_out = df[df[ratio_col] > hi]
            flags.append((f"Low {ratio_col}", low_out))
            flags.append((f"High {ratio_col}", high_out))

# Cột hiển thị: chỉ lấy cột thực sự tồn tại
base_cols = [
    "account",
    "title",
    "followers",
    "views_avg",
    "likes_avg",
    "comments_avg",
    "shares_avg",
    "engagement_per_view",
    "engagement_per_1k_followers",
    "kol_score",
    "like_view_ratio",
    "comment_view_ratio",
    "share_view_ratio",
    "follower_tier",
    "country",
]

for name, sub in flags:
    if sub.empty:
        continue
    display_cols = [c for c in base_cols if c in sub.columns]

    # Chọn khóa sort khả dụng
    if any(k in name for k in ["like_view_ratio", "comment_view_ratio", "share_view_ratio"]):
        sort_candidates = [
            c
            for c in ["like_view_ratio", "comment_view_ratio", "share_view_ratio", "kol_score"]
            if c in sub.columns
        ]
    else:
        sort_candidates = ["kol_score"] if "kol_score" in sub.columns else display_cols[:1]
    sort_key = sort_candidates[0] if sort_candidates else None

    st.markdown(f"**{name}** — up to 200 rows")
    if sort_key:
        st.dataframe(
            sub[display_cols].sort_values(sort_key, ascending=False).head(200),
            use_container_width=True,
        )
    else:
        st.dataframe(sub[display_cols].head(200), use_container_width=True)

st.info(
    "Cách dùng: Low like/view lặp lại → content/traffic kém chất lượng; High ratios → nội dung rất tốt (nhưng cần kiểm chứng thêm bằng lịch sử/case)."
)

# Dùng df (Insights) hoặc dff (Leaderboard đã lọc). Ưu tiên dùng dff nếu bạn muốn shortlist theo filter hiện tại.
base = df

# An toàn: bỏ NA cột cần dùng
need_cols = ["engagement_per_view", "engagement_per_1k_followers", "followers"]
ok = all(c in base.columns for c in need_cols)
if not ok or base[need_cols].dropna().empty:
    st.info("Không đủ cột hoặc dữ liệu để tạo shortlist.")
else:
    # Ngưỡng phân vị (có thể chỉnh 0.75 → 0.8/0.9 tùy chiến dịch)
    thr_epv = base["engagement_per_view"].quantile(0.75)
    thr_ep1k = base["engagement_per_1k_followers"].quantile(0.75)
    thr_f = base["followers"].quantile(0.90)

    # Guardrail đơn giản cho awareness (nếu có)
    min_like_view = (
        base.get("like_view_ratio", pd.Series([0.0] * len(base))).quantile(0.25)
        if "like_view_ratio" in base.columns
        else 0.0
    )

    # 1) Performance-first: EPV & EP1k cùng cao
    perf = base[
        (base["engagement_per_view"] >= thr_epv) & (base["engagement_per_1k_followers"] >= thr_ep1k)
    ].copy()
    if "kol_score" in perf.columns:
        perf = perf.sort_values("kol_score", ascending=False)
    st.subheader("💥 Shortlist: Performance-first (EPV & EP1k top 25%)")
    st.caption(f"Ngưỡng: EPV ≥ {thr_epv:.4f}, EP1k ≥ {thr_ep1k:.4f}")
    st.dataframe(perf.head(300), use_container_width=True)

    # 2) Awareness-first: Reach lớn + tối thiểu like/view
    awar = base[base["followers"] >= thr_f].copy()
    if "like_view_ratio" in base.columns:
        awar = awar[awar["like_view_ratio"] >= min_like_view]
        st.caption(f"Guardrail like/view ≥ Q1 ({min_like_view:.4f}) để tránh reach 'rỗng'.")

    if "followers" in awar.columns:
        awar = awar.sort_values("followers", ascending=False)

    st.subheader("📣 Shortlist: Awareness-first (Top 10% followers + guardrail)")
    st.dataframe(awar.head(300), use_container_width=True)

    # Nút tải xuống nhanh (tùy chọn)
    st.download_button(
        "Download Performance-first (CSV)",
        data=perf.to_csv(index=False).encode("utf-8"),
        file_name="shortlist_performance.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Awareness-first (CSV)",
        data=awar.to_csv(index=False).encode("utf-8"),
        file_name="shortlist_awareness.csv",
        mime="text/csv",
    )

# --- Narrative: tóm tắt insight bằng ngôn ngữ tự nhiên ---

# Tính mức độ tập trung reach (top 10%)
N = len(df)
df_sorted_f = df.sort_values("followers", ascending=False)
total_reach = df["followers"].fillna(0).sum()
top10n = max(1, int(0.10 * N))
top10_reach = df_sorted_f.head(top10n)["followers"].fillna(0).sum()
concentration_10 = 100 * top10_reach / max(total_reach, 1e-9)

# Tóm tắt theo tier (nếu có)
tier_msg = ""
if "follower_tier" in df.columns:
    med = (
        df.groupby("follower_tier")[["engagement_per_view", "engagement_per_1k_followers"]]
        .median()
        .sort_values("engagement_per_1k_followers", ascending=False)
    )
    top_tier = med.index[0] if len(med) else None
    tier_msg = (
        f"Nhóm có hiệu quả nổi bật (theo median EP1k) hiện đang là **{top_tier}**."
        if top_tier
        else ""
    )

# Viết narrative
st.markdown(
    f"""
### 🧠 Tóm tắt nhanh (auto)
- Mức độ tập trung reach: **Top 10% KOL nắm ~{concentration_10:.1f}% tổng follower** ⇒ thị trường { "rất tập trung" if concentration_10>=70 else "tập trung vừa phải" }.
- {tier_msg if tier_msg else "Thiếu cột follower_tier nên không so sánh theo tier."}
- **Gợi ý chiến lược:** kết hợp **Macro/Mega** cho awareness & **Micro/Mid** cho performance.  
- Dùng **Shortlist Performance-first** cho KPI CPA/ROAS; **Shortlist Awareness-first** cho CPM/Reach.
"""
)
