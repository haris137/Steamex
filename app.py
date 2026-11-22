from datetime import date

import streamlit as st

from predictor import THRESHOLD, load_bundle, predict_game

st.set_page_config(page_title="Steamex", page_icon="🎮", layout="wide")

# ---------------------------------------------------------------- styling
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2.5rem; max-width: 1150px;}

.hero h1 {margin: 0; font-size: 2.3rem; letter-spacing: -0.5px;}
.hero p  {margin: .2rem 0 1.4rem 0; color: #8f98a0; font-size: 1.05rem;}

.section-title {font-weight: 600; font-size: 1.02rem; margin: .1rem 0 .15rem 0;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 14px;}

/* keep the result visible while scrolling the inputs (desktop) */
div[data-testid="stColumn"]:has(.result-anchor),
div[data-testid="column"]:has(.result-anchor) {position: sticky; top: 3rem; align-self: flex-start;}

.result-card {border-radius: 18px; padding: 1.7rem 1.6rem; border: 1px solid #2a475e;
              background: linear-gradient(160deg, #1b2838 0%, #14202d 100%);}
.result-card.good {border-color: #4c9a2a; box-shadow: 0 0 30px rgba(92,184,92,.15);}
.result-card.bad  {border-color: #a33e3e; box-shadow: 0 0 30px rgba(217,83,79,.13);}
.result-card .tag     {font-size: .75rem; letter-spacing: 1.5px; text-transform: uppercase; color: #8f98a0;}
.result-card .verdict {font-size: 1.7rem; font-weight: 700; margin: .25rem 0 .6rem 0;}
.result-card.good .verdict {color: #7bd45a;}
.result-card.bad  .verdict {color: #ff7b72;}
.result-card .prob    {font-size: 3.6rem; font-weight: 800; line-height: 1;}
.result-card .sub     {color: #8f98a0; margin: .2rem 0 1.1rem 0;}
.bar  {position: relative; height: 10px; border-radius: 6px; background: #2a475e;}
.bar .fill {height: 100%; border-radius: 6px;}
.good .bar .fill {background: linear-gradient(90deg, #4c9a2a, #7bd45a);}
.bad  .bar .fill {background: linear-gradient(90deg, #a33e3e, #ff7b72);}
.bar .mark {position: absolute; top: -4px; width: 2px; height: 18px; background: #e6edf3; opacity: .7;}
.bar-labels {display: flex; justify-content: space-between; font-size: .75rem; color: #8f98a0; margin-top: .35rem;}
.result-card .note {margin-top: 1rem; font-size: .9rem; color: #c7d5e0;}
.recap {color: #8f98a0; font-size: .88rem; margin-top: .9rem; line-height: 1.5;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading the model...")
def get_bundle():
    return load_bundle()


bundle = get_bundle()

# ---------------------------------------------------------------- header
st.markdown(
    '<div class="hero"><h1>Steamex</h1>'
    "<p>Describe a Steam game, even one that isn't released yet, and the model estimates "
    "how likely players are to love it.</p></div>",
    unsafe_allow_html=True,
)

PRICES = [0.99, 1.99, 2.99, 4.99, 7.99, 9.99, 14.99, 19.99, 24.99, 29.99, 39.99, 49.99, 59.99, 69.99]
AGES = {0: "Everyone", 12: "12+", 16: "16+", 18: "18+"}
THIS_YEAR = date.today().year

left, right = st.columns([3, 2], gap="large")

# ---------------------------------------------------------------- inputs (left)
with left:
    with st.container(border=True):
        st.markdown('<div class="section-title">💰 Price</div>', unsafe_allow_html=True)
        price_type = st.radio("Price type", ["Paid", "Free"], horizontal=True, label_visibility="collapsed")
        is_free = price_type == "Free"
        if is_free:
            price = 0.0
        else:
            price = st.select_slider("Price (USD)", options=PRICES, value=19.99, format_func=lambda p: f"${p:.2f}")

    with st.container(border=True):
        st.markdown('<div class="section-title">🏷️ Genres</div>', unsafe_allow_html=True)
        genres = st.pills("Genres", bundle["genre_options"], selection_mode="multi",
                          label_visibility="collapsed", help="Pick all that apply") or []

    with st.container(border=True):
        st.markdown('<div class="section-title">🎛️ Game features</div>', unsafe_allow_html=True)
        categories = st.pills("Game features", bundle["category_options"], selection_mode="multi",
                              label_visibility="collapsed", help="Pick all that apply") or []

    with st.container(border=True):
        st.markdown('<div class="section-title">🖥️ Platforms</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        windows = c1.checkbox("Windows", value=True)
        mac = c2.checkbox("Mac")
        linux = c3.checkbox("Linux")

    with st.container(border=True):
        st.markdown('<div class="section-title">⚙️ Details</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        n_languages = d1.slider("Supported languages", 1, 40, 5)
        achievements = d2.slider("Achievements", 0, 200, 20, step=5)
        release_year = d1.slider("Release year", 2006, THIS_YEAR + 1, THIS_YEAR)
        required_age = d2.select_slider("Age rating", options=list(AGES), value=0, format_func=AGES.get)

# ---------------------------------------------------------------- result (right)
with right:
    st.markdown('<span class="result-anchor"></span>', unsafe_allow_html=True)

    if not (windows or mac or linux):
        st.info("Select at least one platform to see a prediction.")
    else:
        result = predict_game(bundle["model"], is_free, price, genres, categories,
                              windows, mac, linux, n_languages, required_age, achievements, release_year)
        p = result["probability"]
        good = result["worth_playing"]
        icon = "✅" if good else "❌"
        note = ""
        if abs(p - THRESHOLD) <= 0.05:
            note = "This is a close call, small changes to the inputs could flip the verdict."
        elif not genres:
            note = "Tip: pick at least one genre for a more useful estimate."

        st.markdown(f"""
<div class="result-card {'good' if good else 'bad'}">
  <div class="tag">Prediction</div>
  <div class="verdict">{icon} {result['verdict']}</div>
  <div class="prob">{p:.0%}</div>
  <div class="sub">chance of {bundle['good_ratio']}%+ positive reviews</div>
  <div class="bar"><div class="fill" style="width:{p*100:.0f}%"></div><div class="mark" style="left:{THRESHOLD*100:.0f}%"></div></div>
  <div class="bar-labels"><span>0%</span><span>{THRESHOLD:.0%} = worth playing</span><span>100%</span></div>
  {f'<div class="note">{note}</div>' if note else ''}
</div>""", unsafe_allow_html=True)

        platforms = ", ".join(n for n, on in [("Windows", windows), ("Mac", mac), ("Linux", linux)] if on)
        recap = [("Free" if is_free else f"${price:.2f}"),
                 ", ".join(genres) or "no genre selected",
                 platforms,
                 f"released {release_year}"]
        st.markdown(f'<div class="recap">{" · ".join(recap)}</div>', unsafe_allow_html=True)

st.divider()
st.caption(
    f"**How to read this:** \"worth playing\" means at least {bundle['good_ratio']}% positive Steam reviews "
    f"(and {bundle['min_reviews']}+ reviews). The model only sees basic facts like price, genres and platforms, "
    "so treat the result as a helpful hint, not a guarantee."
)
