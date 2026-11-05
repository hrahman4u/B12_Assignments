import os
import asyncio
import streamlit as st
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Page configuration
st.set_page_config(
    page_title="AutoGen Weather News Agent",
    page_icon="🌦️",
    layout="centered"
)

# Initialize session state for search history if it doesn't exist
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Custom styling for a polished look and text wrapping
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0083b0 0%, #00b4db 100%);
        color: white;
    }
    .wrapped-box {
        background-color: #f8f9fa;
        color: #2d3748;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
        word-break: break-word;
        overflow-x: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2d3748;'>🌦️ AutoGen Weather News Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #718096;'>Get today's weather news for any city in exactly 3 short lines using AutoGen and DuckDuckGo search.</p>", unsafe_allow_html=True)
st.divider()

# Sidebar status check and history view
with st.sidebar:
    st.header("⚙️ Configuration Status")
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_present:
        st.success("OpenAI API Key: **Loaded**")
    else:
        st.error("OpenAI API Key: **Missing**")
        
    st.markdown("---")
    st.markdown("### 🕒 Recent City History")
    if st.session_state.search_history:
        for idx, item in enumerate(st.session_state.search_history, 1):
            st.markdown(f"**{idx}. {item['city']}**")
    else:
        st.info("No searches yet.")
        
    st.markdown("---")
    st.markdown("### 💡 Assignment Details")
    st.markdown("- **Framework:** AutoGen (v0.4+)[cite: 2]")
    st.markdown("- **Model:** gpt-4o-mini[cite: 2]")
    st.markdown("- **Tool:** Keyless DuckDuckGo Web Search (`DDGS().text`)")

# Using a form so pressing Enter inside the text input submits the query automatically
with st.form(key="weather_form"):
    city = st.text_input(
        "Which city would you like weather news for?",
        value="Perth",
        placeholder="e.g., London, Tokyo, Perth"
    )
    
    # Submit button inside the form triggers on Enter or click
    submit_button = st.form_submit_button(label="🚀 Get Weather News")

# Main logic execution triggered either by Enter (form submission) or the button
if submit_button:
    if not api_key_present:
        st.error("⚠️ Please set your `OPENAI_API_KEY` environment variable before running the app.")
    elif not city.strip():
        st.error("⚠️ Please enter a valid city name.")
    else:
        with st.spinner(f"🤖 AutoGen Weather News Agent is searching for today's weather in '{city}'..."):
            
            # FIXED: Switched from .news() to .text() for reliable web retrieval
            def search_weather_news(query_city: str) -> str:
                """Search the web for today's weather conditions in the specified city."""
                results = DDGS().text(query=f"{query_city} weather today forecast", max_results=5)
                return str(results)

            # Define an async function to run the AutoGen agent workflow
            async def run_weather_agent():
                model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
                
                agent = AssistantAgent(
                    name="weather_news",
                    model_client=model_client,
                    tools=[search_weather_news],
                    system_message=(
                        "You are a helpful weather news assistant. "
                        "When given a city, use the search tool to find today's weather conditions "
                        "and reply in exactly 3 short lines."
                    ),
                    reflect_on_tool_use=True
                )
                
                result = await agent.run(task=f"Give me today's weather news for {city}.")
                await model_client.close()
                return result.messages[-1].content

            try:
                # Streamlit-safe event loop execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                weather_reply = loop.run_until_complete(run_weather_agent())
                
                # Save to history (keep only the last 3 items)
                st.session_state.search_history.insert(0, {
                    "city": city,
                    "result": weather_reply
                })
                if len(st.session_state.search_history) > 3:
                    st.session_state.search_history.pop()
                
                st.success("✨ Weather News Generated Successfully!")
                st.markdown(f"### 📋 3-Line Reply for: {city}")
                
                # Render inside text-wrapping container
                st.markdown(f'<div class="wrapped-box">{weather_reply}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

# Display History Section on the Main Page with text wrapping
if st.session_state.search_history:
    st.divider()
    st.subheader("📜 Last 3 Search Results History")
    for idx, hist in enumerate(st.session_state.search_history, 1):
        with st.expander(f"Search #{idx}: {hist['city']}"):
            st.markdown(f'<div class="wrapped-box">{hist["result"]}</div>', unsafe_allow_html=True)