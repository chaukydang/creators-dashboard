# app/utils.py
import pandas as pd, numpy as np, streamlit as st
from pathlib import Path

@st.cache_data
def load_data(path: str = "kol_clean.csv") -> pd.DataFrame:
    # thử nhiều vị trí để chạy được cả local & cloud
    here = Path(__file__).parent
    candidates = [Path(path), here/path, here/"../out/kol_clean.csv", Path.cwd()/path, Path.cwd()/"out/kol_clean.csv"]
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            for c in ["followers","views_avg","likes_avg","comments_avg","shares_avg",
                      "engagement_per_view","engagement_per_1k_followers","kol_score"]:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
            if "followers" in df.columns:
                bins=[-1,1e4,1e5,1e6,1e7,np.inf]
                labels=["Nano (<10k)","Micro (10k-100k)","Mid (100k-1M)","Macro (1M-10M)","Mega (10M+)"]
                df["follower_tier"]=pd.cut(df["followers"], bins=bins, labels=labels)
            else:
                df["follower_tier"]="Unknown"
            return df
    raise FileNotFoundError("kol_clean.csv not found. Put it in app/ or out/.")

def kpi_fmt(x, digits=4):
    import pandas as pd
    return "—" if x is None or pd.isna(x) else f"{x:,.{digits}f}"

def number_fmt(x):
    import pandas as pd
    return "—" if x is None or pd.isna(x) else f"{x:,.0f}"
