
import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

st.set_page_config(
    page_title="LuxeStayz | AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background: linear-gradient(145deg, #f4f8f5 0%, #eaf3f0 48%, #f9f5ec 100%);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1120px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

#MainMenu, footer, header {visibility: hidden;}

.brand {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: #174c43;
}

.hero {
    background: linear-gradient(120deg, #A2845E 100%);
    padding: 3.5rem 3rem;
    border-radius: 28px;
    color: white;
    margin: 1.2rem 0 1.5rem 0;
    box-shadow: 0 16px 38px rgba(23, 76, 67, 0.16);
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.76rem;
    font-weight: 700;
    color: #c7e7d8;
}

.hero h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.4rem, 5vw, 4.2rem);
    line-height: 1.12;
    color: white;
    margin: 1rem 0;
}

.hero p {
    color: #e0eee8;
    font-size: 1.08rem;
    max-width: 610px;
    line-height: 1.8;
}

.feature {
    background: rgba(255,255,255,0.78);
    border: 1px solid #dce9e2;
    border-radius: 16px;
    padding: 1.1rem;
    min-height: 110px;
    margin-bottom: 1.2rem;
}

.feature-title {
    color: #174c43;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.feature-text {
    color: #65766f;
    font-size: 0.9rem;
}

.section-title {
    font-family: 'Playfair Display', Georgia, serif;
    color: #173f36;
    font-size: 1.9rem;
    margin: 1.5rem 0 0.4rem 0;
}

.section-subtitle {
    color: #6a7c74;
    margin-bottom: 1.2rem;
}

.stTextInput label {
    color: #234d43 !important;
    font-weight: 700 !important;
}

.stTextInput input {
    background: white !important;
    border: 1px solid #cfdfd6 !important;
    border-radius: 12px !important;
    min-height: 3.2rem;
}

.stTextInput input:focus {
    border-color: #36816d !important;
    box-shadow: 0 0 0 2px rgba(54,129,109,0.12) !important;
}

.stButton > button {
    background: #174c43;
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 3.2rem;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #287361;
    color: white;
    transform: translateY(-1px);
}

.result-heading {
    font-family: 'Playfair Display', Georgia, serif;
    color: #173f36;
    font-size: 2rem;
    margin-top: 1.8rem;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.88);
    border: 1px solid #dce9e2;
    border-radius: 18px;
}

.footer {
    text-align: center;
    color: #71837a;
    font-size: 0.85rem;
    padding-top: 2.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- BRAND ----------
st.markdown(
    '<div class="brand">✈ LuxeStaysz  <span style="font-weight:400;color:#71837a;">'
    ' &nbsp; / &nbsp; YOUR AI TRAVEL COMPANION</span></div>',
    unsafe_allow_html=True,
)

# ---------- HERO ----------
st.markdown("""
<div class="hero">

   <p>
        Discover facts about the places you have always wanted to visit. Get a curated list of three attractions in your chosen city, complete with reasons to visit and practical tips for each.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------- FEATURE CARDS ----------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature">
        <div class="feature-title">🗺️ Curated Places</div>
        <div class="feature-text">Three interesting attractions selected for your destination.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature">
        <div class="feature-title">💡 Local Insights</div>
        <div class="feature-text">Learn what makes each place worth visiting.</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature">
        <div class="feature-title">🎒 Travel Smarter</div>
        <div class="feature-text">Get a practical tip for every recommended attraction.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- DESTINATION SEARCH ----------
st.markdown(
    '<div class="section-title">Choose your destination</div>'
    '<div class="section-subtitle">One city. Three places to discover. Endless memories.</div>',
    unsafe_allow_html=True,
)

with st.form("travel_form"):
    city = st.text_input(
        "Where would you like to explore?",
        placeholder="Try Chennai, Jaipur, Mumbai, Paris...",
    )
    submitted = st.form_submit_button(
        "✈  Discover My Destination",
        use_container_width=True,
    )

# ---------- CREWAI ----------
if submitted:
    city = city.strip()
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL", "openai/gpt-4o-mini")

    if not city:
        st.warning("Please enter a destination to begin your journey.")
    elif not api_key:
        st.error("OPENAI_API_KEY is missing. Please check your .env file.")
    else:
        with st.spinner(f"✨ Exploring the best of {city}..."):
            try:
                planner = Agent(
                    role="Travel Planner",
                    goal=(
                        "Recommend exactly three interesting places to visit "
                        "in the city requested by the user."
                    ),
                    backstory=(
                        "You are a knowledgeable and enthusiastic travel planner. "
                        "You help visitors discover worthwhile attractions with "
                        "concise explanations and useful travel tips."
                    ),
                    llm=LLM(
                        model=model_name,
                        api_key=api_key,
                    ),
                    verbose=True,
                )

                task = Task(
                    description=(
                        f"Create a travel guide for {city}. Recommend exactly "
                        "three real places to visit. For each, provide the "
                        "place name, why it is worth visiting, and one practical "
                        "visiting tip. Use clear headings and concise details. "
                        "Do not invent opening hours or prices."
                    ),
                    expected_output=(
                        "Exactly three numbered recommendations. Each must "
                        "include a place name, a reason to visit, and a practical "
                        "tip. No lengthy introduction or conclusion."
                    ),
                    agent=planner,
                )

                crew = Crew(
                    agents=[planner],
                    tasks=[task],
                    verbose=True,
                )

                result = crew.kickoff()

                st.markdown(
                    f'<div class="result-heading">Your {city} escape 🌿</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "Your personalized inspiration for the journey ahead."
                )

                with st.container(border=True):
                    st.markdown(str(result))

                st.caption(
                    "LuxeStaysz AI · Verify current opening hours and travel "
                    "details before visiting."
                )

            except Exception as e:
                st.error(f"We couldn't create your travel plan: {e}")

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    TRAVEL IS PASSION 🌍<br>
    <span>LuxeStaysz · Powered by CrewAI and Streamlit</span>
</div>
""", unsafe_allow_html=True)
