"""Loads the trained model and turns a game description into a prediction.

Kept separate from the UI so you can reuse it anywhere (another UI, an API, a script).
"""
from datetime import date
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).parent / "worth_playing_model.joblib"
THRESHOLD = 0.5      # probability at or above this = "worth playing"


def load_bundle(path=MODEL_PATH):
    """Returns a dict with: model, genre_options, category_options, good_ratio, min_reviews."""
    return joblib.load(path)


def predict_game(model, is_free, price_usd=0.0, genres=(), categories=(),
                 windows=True, mac=False, linux=False,
                 n_languages=1, required_age=0, achievements=0, release_year=None):
    """Describe a game -> get a verdict. genres / categories are lists of text, e.g. ["Action", "Indie"]."""
    if is_free:
        price_usd = 0.0
    game = pd.DataFrame([{
        "is_free":      int(is_free),
        "price_usd":    float(price_usd),
        "windows":      int(windows),
        "mac":          int(mac),
        "linux":        int(linux),
        "n_languages":  n_languages,
        "required_age": required_age,
        "achievements": achievements,
        "release_year": release_year or date.today().year,
        "genres":       ",".join(genres),          # ["Action", "Indie"] -> "Action,Indie"
        "categories":   ",".join(categories),
    }])
    probability = float(model.predict_proba(game)[0, 1])
    worth = probability >= THRESHOLD
    return {"worth_playing": worth,
            "probability": round(probability, 3),
            "verdict": "Worth playing" if worth else "Not worth playing"}
