import pandas as pd

from scripts.kol_cleaner import clean_col


def test_clean_col_normalizes_names():
    assert clean_col("Likes Avg%") == "likes_avgpct"
    assert clean_col("Followers-Count") == "followers_count"


def test_epv_ep1k_non_negative(tmp_path, monkeypatch):
    # fake raw
    df = pd.DataFrame(
        {
            "followers": [1000, 0, 50000],
            "views_avg": [10000, 0, 20000],
            "likes_avg": [100, 5, 600],
            "comments_avg": [10, 0, 44],
            "shares_avg": [5, 0, 11],
            "account": ["a", "b", "c"],
        }
    )
    raw = tmp_path / "raw.csv"
    out = tmp_path / "out.csv"
    df.to_csv(raw, index=False)

    # monkeypatch constants in kol_cleaner
    import scripts.kol_cleaner as kc

    kc.RAW = raw
    kc.OUT = out

    kc.main()
    clean = pd.read_csv(out)
    assert (clean["engagement_per_view"].fillna(0) >= 0).all()
    assert (clean["engagement_per_1k_followers"].fillna(0) >= 0).all()
