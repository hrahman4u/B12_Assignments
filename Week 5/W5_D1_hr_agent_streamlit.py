import os
import asyncio
import streamlit as st
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Page configuration
st.set_page_config(
    page_title="AutoGen HR Assistant",
    page_icon="👔",
    layout="centered"
)

# Custom styling for a polished look
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5a6fd6 0%, #683d90 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #4a5568;'>👔 AutoGen HR Assistant App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #718096;'>Generate a 5-line job description for any role using an AutoGen AssistantAgent.</p>", unsafe_allow_html=True)
st.divider()

# Sidebar status check
with st.sidebar:
    st.header("⚙️ Configuration Status")
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_present:
        st.success("OpenAI API Key: **Loaded**")
    else:
        st.error("OpenAI API Key: **Missing**")
    st.markdown("---")
    st.markdown("### 💡 Assignment Details")
    st.markdown("- **Framework:** AutoGen (v0.4+)")
    st.markdown("- **Model:** gpt-4o-mini[cite: 2]")
    st.markdown("- **System Message:** `You are an HR assistant.`[cite: 1, 2]")

# User Input for Job Role
job_title = st.text_input(
    "Enter the job role you want a description for:",
    value="Junior Python Developer",
    placeholder="e.g., Data Scientist, Frontend Developer, DevOps Engineer"
)

# Main button to trigger the agent
if st.button("🚀 Generate Job Description"):
    if not api_key_present:
        st.error("⚠️ Please set your `OPENAI_API_KEY` environment variable before running the agent.")
    elif not job_title.strip():
        st.error("⚠️ Please enter a valid job role.")
    else:
        with st.spinner(f"🤖 AutoGen HR Assistant is generating a job description for '{job_title}'..."):
            
            # Define an async function to run the AutoGen agent workflow
            async def run_hr_agent():
                # 1. Initialize the model client
                model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
                
                # 2. Create the AssistantAgent with the exact required system message
                agent = AssistantAgent(
                    name="hr_assistant",
                    model_client=model_client,
                    system_message="You are an HR assistant."
                )
                
                # 3. Define the prompt dynamically using user input
                task_prompt = (
                    f"Write a 5-line job description for a {job_title}. "
                    "Provide exactly five numbered bullet points or sentences and nothing more."
                )
                
                # 4. Run the agent and collect the result
                result = await agent.run(task=task_prompt)
                
                # 5. Cleanly close the model client to prevent hanging
                await model_client.close()
                
                # Return the final text from the messages list
                return result.messages[-1].content

            try:
                # Execute the async function in Streamlit
                job_description = asyncio.run(run_hr_agent())
                
                st.success("✨ Job Description Generated Successfully!")
                st.markdown(f"### 📋 Final Output for: {job_title}")
                st.code(job_description, language="text")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")