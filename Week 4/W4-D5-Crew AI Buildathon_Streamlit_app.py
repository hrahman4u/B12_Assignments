import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load API keys from environment variables / .env
load_dotenv()

st.set_page_config(
    page_title="Multi-Agent Customer Support",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Multi-Agent Customer Support System")
st.write("A sequential CrewAI support system running an internal Assistant, a Web Search Assistant, and an Entry Agent.")

# API Key Validation
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

if not openai_api_key or not serper_api_key:
    st.warning("⚠️ Missing API keys. Please ensure `OPENAI_API_KEY` and `SERPER_API_KEY` are configured.")

# User Query Input
user_query = st.text_input("Enter your support query or task:", placeholder="e.g., How do I reset my password?")

if st.button("Submit Query", type="primary"):
    if not user_query.strip():
        st.error("Please enter a query before submitting.")
    elif not openai_api_key or not serper_api_key:
        st.error("Cannot run the crew without valid API keys set in your environment.")
    else:
        with st.spinner("Support crew is processing your request sequentially..."):
            try:
                # 1. Search Tool
                search_tool = SerperDevTool()

                # 2. Define the Three Agents
                assistant_agent = Agent(
                    role="Assistant",
                    goal="Answer customer support queries directly based purely on internal knowledge and standard best practices.",
                    backstory="You are a helpful customer support agent capable of providing direct, concise, and structured answers immediately from your own expertise.",
                    verbose=True
                )

                web_search_agent = Agent(
                    role="Web Search Assistant",
                    goal="Search the web for up-to-date and accurate external solutions regarding the user's issue.",
                    backstory="You are an expert technical researcher skilled at querying online sources and synthesizing relevant search results into clear guidance.",
                    tools=[search_tool],
                    verbose=True
                )

                entry_agent = Agent(
                    role="Entry Agent",
                    goal="Collect the query and both answers, write them to a text file, and format both answers clearly for the user UI.",
                    backstory="You are a documentation and logging specialist responsible for logging customer interactions into files and formatting user-facing summaries.",
                    verbose=True
                )

                # 3. Define the Sequential Tasks
                task1_internal = Task(
                    description=f"Provide a direct customer support answer to the following query based on your own knowledge:\nQuery: {user_query}",
                    expected_output="A direct, clear answer to the query without performing any web search.",
                    agent=assistant_agent
                )

                task2_search = Task(
                    description=f"Use the web search tool to find the most accurate external documentation or solution for the following query:\nQuery: {user_query}",
                    expected_output="A comprehensive answer synthesized from web search results.",
                    agent=web_search_agent
                )

                task3_entry = Task(
                    description=(
                        f"Take the original query: '{user_query}', the Assistant's answer from Task 1, and the Web Search Assistant's answer from Task 2.\n"
                        "1. Write the original query, Answer 1 (Assistant), and Answer 2 (Web Search Assistant) into a file named 'answers.txt'.\n"
                        "2. Return both answers clearly separated with headers exactly as follows:\n\n"
                        "### Assistant Answer\n<Insert Answer 1>\n\n"
                        "### Web Search Answer\n<Insert Answer 2>"
                    ),
                    expected_output="Both the Assistant answer and the Web Search answer formatted with markdown headers.",
                    agent=entry_agent,
                    context=[task1_internal, task2_search]
                )

                # 4. Crew Assembly (Sequential Process)
                crew = Crew(
                    agents=[assistant_agent, web_search_agent, entry_agent],
                    tasks=[task1_internal, task2_search, task3_entry],
                    process=Process.sequential,
                    verbose=True
                )

                # Execute the crew
                crew_result = crew.kickoff()

                # Ensure answers.txt is written if tool restrictions apply to file-writing
                ans1_text = str(task1_internal.output.raw if hasattr(task1_internal, 'output') and task1_internal.output else task1_internal.output)
                ans2_text = str(task2_search.output.raw if hasattr(task2_search, 'output') and task2_search.output else task2_search.output)
                
                with open("answers.txt", "w", encoding="utf-8") as f:
                    f.write(f"Query: {user_query}\n\n")
                    f.write(f"--- Assistant Answer ---\n{ans1_text}\n\n")
                    f.write(f"--- Web Search Answer ---\n{ans2_text}\n")

                st.success("Interaction processed and logged to `answers.txt` successfully!")

                # 5. Display Both Answers in the UI
                st.subheader("💡 Assistant Answer (Internal Knowledge)")
                st.info(ans1_text)

                st.subheader("🌐 Web Search Assistant Answer (Web Results)")
                st.info(ans2_text)

            except Exception as e:
                st.error(f"An error occurred during crew execution: {e}")