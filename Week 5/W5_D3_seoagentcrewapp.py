import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent SEO Studio",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for clean text wrapping and card styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        color: white;
    }
    .wrapped-box {
        background-color: #f8fafc;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.2rem;
        white-space: pre-wrap;
        word-break: break-word;
        overflow-x: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1e293b;'>🚀 Multi-Agent SEO Content Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Powered by 4 Sequential AutoGen Agents: Researcher → Writer → SEO Optimizer → Reviewer</p>", unsafe_allow_html=True)
st.divider()

# Sidebar status & pipeline overview
with st.sidebar:
    st.header("⚙️ System Status")
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_present:
        st.success("OpenAI API Key: **Loaded**")
    else:
        st.error("OpenAI API Key: **Missing**")

    st.markdown("---")
    st.markdown("### 🤖 4-Agent Pipeline")
    st.markdown("1. **🔍 Trend Researcher:** Finds a trending subtopic via web search.")
    st.markdown("2. **✍️ Content Writer:** Writes a structured article on that subtopic.")
    st.markdown("3. **📈 SEO Specialist:** Optimizes keywords, headings & meta tags.")
    st.markdown("4. **🧐 Content Reviewer:** Final polish & quality assurance.")

# Web Search Tool for Agent 1
def search_trending_topic(topic: str) -> str:
    """Search the web for current trends, news, and popular subtopics related to the given topic."""
    results = DDGS().text(query=f"{topic} latest trends 2026 popular subtopics", max_results=5)
    return str(results)

# Async Multi-Agent Workflow
async def run_seo_pipeline(user_topic: str):
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Agent 1: Trend Researcher
    researcher = AssistantAgent(
        name="Trend_Researcher",
        model_client=model_client,
        tools=[search_trending_topic],
        system_message=(
            "You are an expert Market & Trend Researcher. "
            "Use the `search_trending_topic` tool to research the user's topic. "
            "Identify ONE specific, high-potential trending subtopic within it, along with "
            "3-5 target SEO keywords and key factual points. Keep your brief concise and structured."
        ),
        reflect_on_tool_use=True
    )

    # Agent 2: Content Writer
    writer = AssistantAgent(
        name="Content_Writer",
        model_client=model_client,
        system_message=(
            "You are an expert Blog & Article Writer. "
            "Based ONLY on the trending subtopic and keywords provided by Trend_Researcher, "
            "write an engaging, well-structured 300-400 word blog post with a catchy title and subheadings."
        )
    )

    # Agent 3: SEO Specialist
    seo_specialist = AssistantAgent(
        name="SEO_Specialist",
        model_client=model_client,
        system_message=(
            "You are a Technical & On-Page SEO Specialist. "
            "Review the draft written by Content_Writer. Check and correct the SEO by: "
            "1) Adding an SEO Meta Title (under 60 chars) and Meta Description (under 155 chars) at the top. "
            "2) Ensuring primary keywords appear naturally in the H1 title, H2 subheadings, and first paragraph. "
            "3) Improving readability and scannability. Return the full SEO-corrected article."
        )
    )

    # Agent 4: Final Content Reviewer
    reviewer = AssistantAgent(
        name="Content_Reviewer",
        model_client=model_client,
        system_message=(
            "You are a Senior Editorial Reviewer. "
            "Perform a final quality check on the SEO_Specialist's output. "
            "Fix any grammar issues, awkward phrasing, or keyword stuffing while keeping all SEO improvements intact. "
            "Output ONLY the final, publication-ready article (including the Meta Title and Meta Description)."
        )
    )

    # Run all 4 agents sequentially in a RoundRobinGroupChat
    # Termination: 1 initial user prompt + 4 agent turns (+1 extra turn if researcher uses tool reflection)
    team = RoundRobinGroupChat(
        participants=[researcher, writer, seo_specialist, reviewer],
        termination_condition=MaxMessageTermination(max_messages=6)
    )

    task_prompt = f"Research a trending subtopic for '{user_topic}', write an article, optimize its SEO, and review it."
    result = await team.run(task=task_prompt)
    await model_client.close()

    # Extract each agent's contribution from the conversation messages
    outputs = {}
    for msg in result.messages:
        if msg.source in ["Trend_Researcher", "Content_Writer", "SEO_Specialist", "Content_Reviewer"]:
            outputs[msg.source] = msg.content

    return outputs

# Input Form (supports both Enter key and Submit button)
with st.form(key="seo_form"):
    topic_input = st.text_input(
        "Enter any broad topic:",
        placeholder="e.g., Artificial Intelligence, Sustainable Fashion, Personal Finance, Electric Vehicles"
    )
    submit_btn = st.form_submit_button("✨ Generate SEO Content")

if submit_btn:
    if not api_key_present:
        st.error("⚠️ Please set your `OPENAI_API_KEY` in the `.env` file before running.")
    elif not topic_input.strip():
        st.error("⚠️ Please enter a topic first.")
    else:
        with st.spinner(f"🤖 Running 4-Agent SEO Pipeline for '{topic_input}'... This takes ~15–25 seconds."):
            try:
                # Streamlit-safe async execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                agent_outputs = loop.run_until_complete(run_seo_pipeline(topic_input))

                st.success("✅ SEO Content Pipeline Completed!")

                # Display Final Reviewed Article prominently
                st.subheader("🏆 Final Publication-Ready Content (Reviewed)")
                final_article = agent_outputs.get("Content_Reviewer", "No final output generated.")
                st.markdown(f'<div class="wrapped-box">{final_article}</div>', unsafe_allow_html=True)

                st.divider()
                st.subheader("🔍 Inspect Step-by-Step Agent Outputs")

                # Tabs to inspect each agent's work
                tab1, tab2, tab3, tab4 = st.tabs([
                    "1️⃣ Trend Researcher",
                    "2️⃣ Content Writer (Draft)",
                    "3️⃣ SEO Specialist (Optimized)",
                    "4️⃣ Content Reviewer (Final)"
                ])

                with tab1:
                    st.markdown(agent_outputs.get("Trend_Researcher", "No output."))
                with tab2:
                    st.markdown(agent_outputs.get("Content_Writer", "No output."))
                with tab3:
                    st.markdown(agent_outputs.get("SEO_Specialist", "No output."))
                with tab4:
                    st.markdown(agent_outputs.get("Content_Reviewer", "No output."))

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")