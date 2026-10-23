import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Tech Newsletter Crew",
    page_icon="📰",
    layout="centered"
)

# Custom CSS for a colorful and appealing UI
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5a6fd6 0%, #683d90 100%);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #f1f3f5;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header with Emoji and Gradient Style
st.markdown(
    "<h1 style='text-align: center; color: #4a5568;'>📰 AI Tech Newsletter Generator</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #718096;'>Powered by CrewAI (Researcher + Writer agents) & Serper Web Search</p>", 
    unsafe_allow_html=True
)
st.divider()

# Sidebar for API key configurations / checks
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bot.png", width=80)
    st.header("⚙️ System Status")
    
    openai_key_present = bool(os.getenv("OPENAI_API_KEY"))
    serper_key_present = bool(os.getenv("SERPER_API_KEY"))

    if openai_key_present:
        st.success(" OpenAI API Key: **Loaded**")
    else:
        st.error(" OpenAI API Key: **Missing**")

    if serper_key_present:
        st.success(" Serper API Key: **Loaded**")
    else:
        st.error(" Serper API Key: **Missing**")
        
    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.markdown("1. **Researcher Agent** scours the web for today's top 3 tech news.")
    st.markdown("2. **Writer Agent** transforms them into a punchy 5-line newsletter[cite: 1, 2].")

# Main Action Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("🚀 Run Newsletter Crew")

if run_button:
    if not openai_key_present or not serper_key_present:
        st.error("⚠️ Please make sure both `OPENAI_API_KEY` and `SERPER_API_KEY` are set in your `.env` file.")
    else:
        with st.status("🤖 **Crew at Work...**", expanded=True) as status:
            st.write("🔍 **Researcher:** Searching the web for top tech news...")
            try:
                # 1. Initialize the Serper search tool
                search = SerperDevTool()

                # 2. Create the Researcher Agent
                researcher = Agent(
                    role="Tech News Researcher",
                    goal="Find today's top 3 tech news stories by searching the web.",
                    backstory=(
                        "You are an expert tech journalist with a sharp eye for groundbreaking "
                        "innovations, AI breakthroughs, and major industry developments."
                    ),
                    tools=[search],
                    verbose=True
                )

                # 3. Create the Writer Agent
                writer = Agent(
                    role="Tech Newsletter Writer",
                    goal="Transform the researcher's top tech stories into a punchy 5-line newsletter.",
                    backstory=(
                        "You are a master newsletter editor known for making complex tech news "
                        "crisp, engaging, and easy to digest in exactly five lines."
                    ),
                    verbose=True
                )

                # 4. Create the Research Task
                find_task = Task(
                    description=(
                        "Search the web and find today's top 3 tech news stories. "
                        "Provide a clear, clean summary of each story for the writer."
                    ),
                    expected_output=(
                        "A clear summary of today's top 3 tech news stories, including headlines and brief key details."
                    ),
                    agent=researcher
                )

                # 5. Create the Writing Task
                write_task = Task(
                    description=(
                        "Using the top 3 tech stories provided by the researcher, craft a concise tech newsletter. "
                        "The final output must strictly follow this 5-line format:\n"
                        "Tech in 5 lines\n"
                        "1. <first story, one line>\n"
                        "2. <second story, one line>\n"
                        "3. <third story, one line>\n"
                        "Why it matters: <one line>"
                    ),
                    expected_output=(
                        "Exactly 5 lines starting with 'Tech in 5 lines', followed by 3 numbered story lines, "
                        "and concluding with 'Why it matters:'."
                    ),
                    agent=writer,
                    context=[find_task]
                )

                # 6. Assemble the Sequential Crew and Kickoff
                crew = Crew(
                    agents=[researcher, writer],
                    tasks=[find_task, write_task],
                    process=Process.sequential,
                    verbose=True
                )

                st.write("✍️ **Writer:** Drafting your 5-line newsletter...")
                result = crew.kickoff()
                
                status.update(label="✨ **Newsletter Generated Successfully!**", state="complete", expanded=False)

                st.success("🎉 Here is your fresh tech newsletter:")
                st.markdown("### 📋 Final Newsletter")
                st.info(result)

            except Exception as e:
                status.update(label="❌ **Execution Failed**", state="error", expanded=True)
                st.error(f"An error occurred while running the crew: {e}")