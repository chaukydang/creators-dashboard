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


st.set_page_config(page_title="Forecast & Simulation", page_icon="📈", layout="wide")
st.title("📈 Forecast & 🎲 Simulation")

df = U.load_data()
cfg = U.load_config()
sim_cfg = cfg.get("simulation_defaults", {})

# ---------- Forecast (growth toy model) ----------
st.subheader("Forecast (toy growth model)")
colA, colB, colC = st.columns(3)
with colA:
    base_views = float(
        st.number_input(
            "Base daily views (median of dataset)",
            value=float(df.get("views_avg", pd.Series([10000])).median()),
        )
    )
with colB:
    growth = st.slider("Daily growth rate (%)", 0.0, 5.0, 0.5, 0.1)
with colC:
    horizon = st.number_input("Horizon (days)", min_value=7, max_value=90, value=30, step=1)

days = np.arange(horizon)
forecast = base_views * (1 + growth / 100.0) ** days
fig, ax = plt.subplots()
ax.plot(days, forecast)
ax.set_xlabel("Day")
ax.set_ylabel("Views (forecast)")
st.pyplot(fig)

st.caption(
    "Mô hình đơn giản: lũy kế tăng trưởng %/ngày. Có thể thay bằng ARIMA/Prophet nếu có time-series thực tế."
)

# ---------- Campaign Monte Carlo Simulation ----------
st.subheader("Campaign Monte Carlo Simulation")

# chọn danh sách KOL
name_col = "account" if "account" in df.columns else df.columns[0]
multi = st.multiselect(
    "Chọn KOL tham gia campaign", options=df[name_col].astype(str).tolist(), max_selections=30
)

cpv = float(
    st.number_input(
        "Cost per View (USD)", value=float(sim_cfg.get("cpv", 0.02)), step=0.001, format="%.3f"
    )
)
budget = float(
    st.number_input("Budget (USD)", value=float(sim_cfg.get("budget", 5000)), step=100.0)
)
view_to_reach = float(
    st.number_input(
        "View → Reach ratio", value=float(sim_cfg.get("view_to_reach_ratio", 0.85)), step=0.01
    )
)

n_runs = st.slider("Số lần mô phỏng (Monte Carlo)", 100, 5000, 1000, 100)

if st.button("Run simulation", type="primary"):
    if not multi:
        st.warning("Hãy chọn ít nhất 1 KOL.")
        st.stop()

    sub = df[df[name_col].astype(str).isin(multi)].copy()
    if "engagement_per_view" not in sub.columns:
        st.error("Thiếu cột engagement_per_view.")
        st.stop()

    # phân bổ ngân sách đều theo số KOL (có thể thay bằng trọng số followers/kol_score)
    sub["budget_alloc"] = budget / len(sub)
    # view kỳ vọng theo CPV
    sub["exp_views"] = sub["budget_alloc"] / max(cpv, 1e-9)
    # engagement kỳ vọng = views * EPV
    sub["exp_engagements"] = sub["exp_views"] * sub["engagement_per_view"].fillna(0)

    # phương sai: giả định EPV ~ LogNormal với sigma theo độ phân tán dataset
    epv = sub["engagement_per_view"].fillna(1e-9).values
    log_sigma = np.clip(np.log1p(epv.std() / (epv.mean() + 1e-9)), 0.05, 0.6)

    rng = np.random.default_rng(42)
    total_views = []
    total_eng = []
    total_reach = []
    for _ in range(n_runs):
        # sample EPV noise
        noise = rng.lognormal(mean=0.0, sigma=log_sigma, size=len(sub))
        epv_draw = epv * noise
        views_draw = sub["exp_views"].values
        eng_draw = views_draw * epv_draw
        reach_draw = views_draw * view_to_reach

        total_views.append(views_draw.sum())
        total_eng.append(eng_draw.sum())
        total_reach.append(reach_draw.sum())

    def p(x, q):
        return float(np.quantile(x, q))

    res = {
        "views": {
            "P10": p(total_views, 0.1),
            "P50": p(total_views, 0.5),
            "P90": p(total_views, 0.9),
        },
        "engagements": {
            "P10": p(total_eng, 0.1),
            "P50": p(total_eng, 0.5),
            "P90": p(total_eng, 0.9),
        },
        "reach": {
            "P10": p(total_reach, 0.1),
            "P50": p(total_reach, 0.5),
            "P90": p(total_reach, 0.9),
        },
    }
    st.write("**Kết quả mô phỏng (tổng)**")
    st.json(res)

    # bảng chi tiết theo KOL (kỳ vọng)
    view_reach = (sub["exp_views"] * view_to_reach).rename("exp_reach")
    out_table = sub[[name_col, "budget_alloc", "exp_views", "exp_engagements"]].copy()
    out_table["exp_reach"] = view_reach.values
    st.dataframe(out_table, use_container_width=True)

    st.download_button(
        "Download expected table (CSV)",
        data=out_table.to_csv(index=False).encode("utf-8"),
        file_name="simulation_expected.csv",
        mime="text/csv",
    )

st.info(
    "Gợi ý: thay vì phân bổ đều, bạn có thể phân bổ theo `kol_score` hoặc tối ưu hoá (tương lai)."
)
