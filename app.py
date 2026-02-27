import streamlit as st
import pandas as pd

# ---------------- IMPORTS ----------------
from auth import signup_user, login_user
from NM_recommender import (
    nutrition_df,
    recommend_snacks,
    get_user_nutrient_preferences,
    explain_recommendation,
    is_cold_start_user
)
from interaction_logger import log_interaction
from plots import (
    nutrition_radar_chart,
    nutrition_bar_chart,
    sentiment_pie_chart,
    user_nutrient_preference_chart
)
from user_dashboard import (
    get_user_summary,
    get_top_snacks,
    get_recent_activity
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NutriMatch – Healthy Snack Recommender",
    layout="wide",
    page_icon="🍎"
)

# ---------------- SESSION INIT ----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "last_recs" not in st.session_state:
    st.session_state.last_recs = None

if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

# ---------------- LOAD REVIEWS ----------------
@st.cache_data
def load_reviews():
    return pd.read_csv(
        "C:/Users/Chandu/OneDrive/Desktop/NutriMatch/final/merged_reviews_metadata.csv",
        low_memory=False
    )

merged_df = load_reviews()

# ---------------- HEADER ----------------
st.markdown("""
<style>
.header { text-align:center; font-size:40px; font-weight:800; color:#2E7D32; }
.sub { text-align:center; font-size:18px; color:#555; }
.card { background:#F1F8F6; padding:15px; border-radius:12px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>NutriMatch 🍎</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Healthy Snack Recommendation with Personalization</div><br>", unsafe_allow_html=True)

# ---------------- SIDEBAR AUTH ----------------
st.sidebar.header("🔐 User Authentication")

if st.session_state.user_id is None:
    mode = st.sidebar.radio("Choose action", ["Login", "Sign Up"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if mode == "Sign Up" and st.sidebar.button("Create Account"):
        success, msg = signup_user(username, password)
        st.sidebar.success(msg) if success else st.sidebar.error(msg)

    if mode == "Login" and st.sidebar.button("Login"):
        success, result = login_user(username, password)
        if success:
            st.session_state.user_id = result
            st.rerun()
        else:
            st.sidebar.error(result)

else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.last_recs = None
        st.rerun()

# ---------------- PROTECT APP ----------------
if st.session_state.user_id is None:
    st.info("Please log in to use NutriMatch.")
    st.stop()

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["👤 Dashboard", "🔍 Search & Recommend", "📊 Profile"])

# ======================================================
# TAB 1 — DASHBOARD
# ======================================================
with tab1:
    st.markdown("## 👤 Your Dashboard")

    summary = get_user_summary(st.session_state.user_id)
    col1, col2 = st.columns(2)
    col1.metric("Total Interactions", summary["total_interactions"])
    col2.metric("Unique Snacks Explored", summary["unique_foods"])

    st.markdown("### ⭐ Favorite Snacks")
    top_snacks = get_top_snacks(st.session_state.user_id)

    if top_snacks.empty:
        st.info("No interaction history yet.")
    else:
        for _, r in top_snacks.iterrows():
            st.write(f"• **{r['food_name']}** (score: {r['score']:.2f})")

    st.markdown("### 🕒 Recent Activity")
    recent = get_recent_activity(st.session_state.user_id)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True)

# ======================================================
# TAB 2 — SEARCH & RECOMMEND
# ======================================================
with tab2:
    st.markdown("## 🔍 Find Healthy Alternatives")

    food_list = sorted(nutrition_df["food"].unique())
    selected_food = st.selectbox("Choose a snack:", food_list)
    top_n = st.slider("Number of recommendations:", 3, 10, 5)

    if st.button("Get Recommendations"):
        st.session_state.selected_food = selected_food

        log_interaction(st.session_state.user_id, selected_food, "view")

        recs = recommend_snacks(
            selected_food,
            user_id=st.session_state.user_id,
            top_n=top_n
        )

        log_interaction(st.session_state.user_id, selected_food, "recommend")
        st.session_state.last_recs = recs

    if st.session_state.last_recs is not None:
        recs = st.session_state.last_recs
        selected_row = nutrition_df[nutrition_df["food"] == st.session_state.selected_food].iloc[0]
        prefs = get_user_nutrient_preferences(st.session_state.user_id)

        st.markdown("### 🥗 Recommended Alternatives")

        for _, row in recs.iterrows():
            recommended_row = nutrition_df[nutrition_df["food"] == row["food"]].iloc[0]
            explanation = explain_recommendation(selected_row, recommended_row, prefs)

            st.markdown(f"""
            <div class='card'>
                <h4 style='color:#1B5E20'>{row['food']}</h4>
                <b>Hybrid Score:</b> {row['hybrid_score']:.3f}<br>
                <b>Health Score:</b> {row['health_score_norm']:.2f}<br>
                <b>Protein:</b> {row['protein']}g |
                <b>Fiber:</b> {row['fiber']}g |
                <b>Calories:</b> {row['calories']} kcal
                <p><i>🧠 {explanation}</i></p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(nutrition_bar_chart(recommended_row))
            with col2:
                st.pyplot(nutrition_radar_chart(selected_row, recommended_row))

# ======================================================
# TAB 3 — PROFILE
# ======================================================
with tab3:
    st.markdown("## 🧬 Nutrient Preference Profile")

    prefs = get_user_nutrient_preferences(st.session_state.user_id)

    if prefs is None:
        st.info("Explore snacks to build your profile.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Protein", round(prefs["protein"], 2))
            st.metric("Fiber", round(prefs["fiber"], 2))
            st.metric("Fat", round(prefs["fat"], 2))
            st.metric("Calories", round(prefs["calories"], 2))
        with col2:
            st.pyplot(user_nutrient_preference_chart(prefs))
