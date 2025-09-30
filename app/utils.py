# ---- imports ở đầu file (đảm bảo đủ) ----
import os

import numpy as np
import pandas as pd
import streamlit as st
import yaml


# ---- number/kpi format helpers ----
def kpi_fmt(x, digits: int = 4) -> str:
    """Format KPI number with fixed decimals; handle None/NaN gracefully."""
    try:
        import math

        if x is None or (isinstance(x, float) and math.isnan(x)):
            return "—"
        return f"{float(x):,.{digits}f}"
    except Exception:
        return "—"


def number_fmt(x) -> str:
    """Format integer-like values with thousand separators; handle None/NaN."""
    try:
        import math

        if x is None or (isinstance(x, float) and math.isnan(x)):
            return "—"
        return f"{float(x):,.0f}"
    except Exception:
        return "—"


def pct_fmt(x, digits: int = 2) -> str:
    """Format percentage (0.123 -> 12.30%)."""
    try:
        import math

        if x is None or (isinstance(x, float) and math.isnan(x)):
            return "—"
        return f"{100 * float(x):,.{digits}f}%"
    except Exception:
        return "—"


# ---- đọc config.yaml (cache) ----
@st.cache_data(show_spinner=False)
def load_config(path: str = "app/config.yaml") -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


# ---- load_data cứng cáp + uploader fallback (đã cache) ----
@st.cache_data(show_spinner=False)
def load_data():
    candidates = ["out/kol_clean.csv", "kol_clean.csv", "app/out/kol_clean.csv"]
    for p in candidates:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                return df
            except Exception as e:
                st.warning(f"Found {p} but failed to read: {e}")

    st.info("No local clean CSV found. Upload your `kol_clean.csv` below.")
    up = st.file_uploader("Upload kol_clean.csv", type=["csv"])
    if up:
        try:
            df = pd.read_csv(up)
            return df
        except Exception as e:
            st.error(f"Failed to read uploaded file: {e}")
            st.stop()
    st.stop()


# ---- KOL Score có cấu hình trọng số ----
def compute_kol_score(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    w_epv = cfg.get("scoring", {}).get("epv_weight", 0.6)
    w_ep1k = cfg.get("scoring", {}).get("ep1k_weight", 0.4)

    d = df.copy()
    for c in ["engagement_per_view", "engagement_per_1k_followers"]:
        if c not in d.columns:
            d[c] = np.nan

    # scale 0..1 (robust)
    def robust_minmax(s: pd.Series):
        s = s.astype(float)
        q1, q99 = s.quantile(0.01), s.quantile(0.99)
        denom = (q99 - q1) if (q99 - q1) > 0 else 1.0
        return ((s - q1) / denom).clip(0, 1)

    s_epv = robust_minmax(d["engagement_per_view"])
    s_ep1k = robust_minmax(d["engagement_per_1k_followers"])
    d["kol_score"] = (w_epv * s_epv + w_ep1k * s_ep1k).fillna(0)
    return d


# ---- Similarity (nearest by cosine) cho Profile page ----
def top_similar(df: pd.DataFrame, idx: int, features: list, k: int = 10) -> pd.DataFrame:
    d = df.copy()
    for c in features:
        if c not in d.columns:
            d[c] = 0.0
    X = d[features].fillna(0.0).astype(float).values
    # normalize
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    Xn = X / n
    base = Xn[idx : idx + 1]  # shape (1, F)
    sim = Xn @ base.T  # cosine similarity
    d["similarity"] = sim[:, 0]
    out = d.drop(index=d.index[idx]).sort_values("similarity", ascending=False).head(k)
    return out
