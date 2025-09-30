# scripts/kol_cleaner.py
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("./data/tiktok_top_1000.csv")
OUT = Path("./out/kol_clean.csv")


def clean_col(c: str) -> str:
    return (
        c.strip().replace(" ", "_").replace(".", "").replace("%", "pct").replace("-", "_").lower()
    )


def main():
    df = pd.read_csv(RAW)
    df.columns = [clean_col(c) for c in df.columns]

    # map cột có thể khác tên giữa các file
    col_map = {
        "followers": ["subscribers_count", "followers", "follower_cnt"],
        "views_avg": ["views_avg", "avg_views", "view_avg"],
        "likes_avg": ["likes_avg", "avg_likes", "like_avg"],
        "comments_avg": ["comments_avg", "avg_comments", "comment_avg"],
        "shares_avg": ["shares_avg", "avg_shares", "share_avg"],
        "account": ["account", "username", "handle"],
        "title": ["title", "nickname", "display_name"],
        "country": ["country"],
        "link": ["link", "url", "profile_url"],
        "rank": ["rank"],
    }
    resolved = {}
    for std, cands in col_map.items():
        for cand in cands:
            if cand in df.columns:
                resolved[std] = cand
                break

    # ép kiểu số
    for k in ["followers", "views_avg", "likes_avg", "comments_avg", "shares_avg"]:
        if k in resolved:
            c = resolved[k]
            df[c] = pd.to_numeric(
                df[c]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(" ", "", regex=False),
                errors="coerce",
            )

    # KPI: EPV & EP1k
    def safe_div(a, b):
        return a / b.replace(0, np.nan)

    if all(k in resolved for k in ["views_avg", "likes_avg", "comments_avg", "shares_avg"]):
        inter = (
            df[resolved["likes_avg"]].fillna(0)
            + df[resolved["comments_avg"]].fillna(0)
            + df[resolved["shares_avg"]].fillna(0)
        )
        df["engagement_per_view"] = safe_div(inter, df[resolved["views_avg"]])
    else:
        df["engagement_per_view"] = np.nan

    if all(k in resolved for k in ["followers", "likes_avg", "comments_avg", "shares_avg"]):
        inter_f = (
            df[resolved["likes_avg"]].fillna(0)
            + df[resolved["comments_avg"]].fillna(0)
            + df[resolved["shares_avg"]].fillna(0)
        )
        df["engagement_per_1k_followers"] = safe_div(inter_f, df[resolved["followers"]]) * 1000
    else:
        df["engagement_per_1k_followers"] = np.nan

    # KOL score (blend)
    df["kol_score"] = (
        df["engagement_per_view"].fillna(0).rank(pct=True) * 0.6
        + df["engagement_per_1k_followers"].fillna(0).rank(pct=True) * 0.4
    )

    # tỉ lệ để check anomaly
    if "likes_avg" in resolved and "views_avg" in resolved:
        df["like_view_ratio"] = df[resolved["likes_avg"]] / df[resolved["views_avg"]].replace(
            0, np.nan
        )
    if "comments_avg" in resolved and "views_avg" in resolved:
        df["comment_view_ratio"] = df[resolved["comments_avg"]] / df[resolved["views_avg"]].replace(
            0, np.nan
        )
    if "shares_avg" in resolved and "views_avg" in resolved:
        df["share_view_ratio"] = df[resolved["shares_avg"]] / df[resolved["views_avg"]].replace(
            0, np.nan
        )

    # chọn & đổi tên cột chuẩn
    keep = []
    for std in [
        "country",
        "rank",
        "account",
        "title",
        "link",
        "followers",
        "views_avg",
        "likes_avg",
        "comments_avg",
        "shares_avg",
    ]:
        if std in resolved:
            keep.append(resolved[std])
    rename_map = {
        resolved[k]: k
        for k in resolved
        if k
        in [
            "country",
            "rank",
            "account",
            "title",
            "link",
            "followers",
            "views_avg",
            "likes_avg",
            "comments_avg",
            "shares_avg",
        ]
        and resolved.get(k) in keep
    }

    df_clean = df[
        keep
        + [
            "engagement_per_view",
            "engagement_per_1k_followers",
            "kol_score",
            "like_view_ratio",
            "comment_view_ratio",
            "share_view_ratio",
        ]
    ].rename(columns=rename_map)

    # follower tier
    if "followers" in df_clean.columns:
        bins = [-1, 1e4, 1e5, 1e6, 1e7, np.inf]
        labels = [
            "Nano (<10k)",
            "Micro (10k-100k)",
            "Mid (100k-1M)",
            "Macro (1M-10M)",
            "Mega (10M+)",
        ]
        df_clean["follower_tier"] = pd.cut(df_clean["followers"], bins=bins, labels=labels)
    else:
        df_clean["follower_tier"] = "Unknown"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUT, index=False)
    print(f"✅ Saved clean data → {OUT.resolve()} | rows={len(df_clean):,}")


if __name__ == "__main__":
    main()
