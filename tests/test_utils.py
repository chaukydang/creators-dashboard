import pandas as pd

from app.utils import compute_kol_score, top_similar


def test_compute_kol_score_basic():
    df = pd.DataFrame(
        {
            "engagement_per_view": [0.01, 0.02, 0.03],
            "engagement_per_1k_followers": [1.0, 2.0, 3.0],
        }
    )
    cfg = {"scoring": {"epv_weight": 0.6, "ep1k_weight": 0.4}}
    d = compute_kol_score(df, cfg)
    assert "kol_score" in d.columns
    assert (d["kol_score"].between(0, 1)).all()


def test_top_similar_shapes():
    df = pd.DataFrame(
        {
            "engagement_per_view": [0.01, 0.02, 0.03, 0.04],
            "engagement_per_1k_followers": [1, 2, 1, 3],
            "followers": [1000, 5000, 2000, 10000],
            "account": ["a", "b", "c", "d"],
        }
    )
    out = top_similar(
        df, idx=0, features=["engagement_per_view", "engagement_per_1k_followers", "followers"], k=2
    )
    assert len(out) == 2
    assert "similarity" in out.columns
