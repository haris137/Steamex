# 🎮 Is it worth playing? - Streamlit UI

Pick a game's price, genres, features and platforms with a few clicks and get a "worth playing" prediction.

## Run it

You need Python 3.9 - 3.13.

```bash
# 1. (recommended) make a clean environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# 2. install the packages (scikit-learn is pinned to the version the model was trained with)
pip install -r requirements.txt

# 3. start the app
streamlit run app.py
```

It opens at http://localhost:8501.

## What is in this folder

| File | What it does |
|---|---|
| `app.py` | The Streamlit UI (inputs, result card, styling) |
| `predictor.py` | Loads the model and defines `predict_game(...)` |
| `worth_playing_model.joblib` | The trained model + the genre / feature lists used by the UI |
| `requirements.txt` | Packages to install |
| `.streamlit/config.toml` | Dark Steam-style theme |
| `notebook/` | The notebook that trains the model |

## Troubleshooting

- **Error when loading the model** (`_RemainderColsList`, `__setstate__` ...): your scikit-learn version differs from 1.6.1.
  Run `pip install scikit-learn==1.6.1`. If you retrain the model, install the same scikit-learn version you trained with and update `requirements.txt`.
- **`st.pills` not found**: update Streamlit with `pip install -U streamlit`.
