import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load .env with override so fresh keys always take precedence
load_dotenv(override=True)

# Page Configuration
st.set_page_config(
    page_title="Enterprise Multi-Domain Support",
    page_icon="🎧",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.7rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        color: white;
    }
    .response-card {
        background-color: #f8fafc;
        color: #0f172a;
        border-left: 5px solid #2563eb;
        border-radius: 6px;
        padding: 1.25rem;
        white-space: pre-wrap;
        word-break: break-word;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🎧 Enterprise Multi-Domain Support Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Intelligent Manager Routing across AI • Finance • HR • Admin • Compliance</p>", unsafe_allow_html=True)
st.divider()

# Initialize Chat History in Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Status & Agent Directory
with st.sidebar:
    st.header("⚙️ System Status")
    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_present:
        st.success("OpenAI API Key: **Active**")
    else:
        st.error("OpenAI API Key: **Missing**")

    st.markdown("---")
    st.markdown("### 🧭 Support Routing Directory")
    st.markdown("- **👔 Support Manager:** Triages & assigns tickets")
    st.markdown("- **🤖 AI Specialist:** Models, APIs & AI workflows")
    st.markdown("- **💰 Finance Specialist:** Invoices, payroll & expenses")
    st.markdown("- **👥 HR Specialist:** Leave, onboarding & benefits")
    st.markdown("- **🏢 Admin Specialist:** Facilities, IT gear & travel")
    st.markdown("- **⚖️ Compliance Specialist:** Privacy, audits & policies")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Shared formatting standard for consistent customer support experience
CONSISTENT_STYLE_GUIDE = (
    "Maintain a warm, empathetic, and professional enterprise support tone. "
    "Always format your reply consistently with these three sections:\n"
    "1. **Summary & Acknowledgement:** Briefly confirm understanding of the issue.\n"
    "2. **Resolution / Guidance:** Clear, step-by-step answer or policy guidance.\n"
    "3. **Next Steps:** What the user should do next or if escalation is needed.\n"
    "End your response with the exact word TERMINATE on a new line."
)

# Async Multi-Agent Routing Workflow
async def route_and_answer_query(user_query: str):
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # 1. Manager Agent (Triage & Assignment)
    manager = AssistantAgent(
        name="Support_Manager",
        model_client=model_client,
        description="The Support Manager who triages customer queries and assigns them to the right domain specialist.",
        system_message=(
            "You are the Customer Support Triage Manager. "
            "Analyze the customer's query, identify the single most relevant domain "
            "(AI, Finance, HR, Admin, or Compliance), briefly state which specialist you are assigning "
            "the ticket to and why in 1-2 sentences. Do NOT answer the technical/domain question yourself."
        )
    )

    # 2. Domain Specialist Agents
    ai_agent = AssistantAgent(
        name="AI_Support",
        model_client=model_client,
        description="Specialist for Artificial Intelligence, LLM APIs, model errors, prompts, and AI tools.",
        system_message=f"You are the Senior AI Support Specialist. {CONSISTENT_STYLE_GUIDE}"
    )

    finance_agent = AssistantAgent(
        name="Finance_Support",
        model_client=model_client,
        description="Specialist for Finance, billing, invoices, tax, expense reimbursements, budgets, and payroll.",
        system_message=f"You are the Senior Finance Support Specialist. {CONSISTENT_STYLE_GUIDE}"
    )

    hr_agent = AssistantAgent(
        name="HR_Support",
        model_client=model_client,
        description="Specialist for Human Resources, leave policies, onboarding, benefits, hiring, and employee relations.",
        system_message=f"You are the Senior HR Support Specialist. {CONSISTENT_STYLE_GUIDE}"
    )

    admin_agent = AssistantAgent(
        name="Admin_Support",
        model_client=model_client,
        description="Specialist for Administration, office facilities, hardware/laptop requests, access badges, and travel bookings.",
        system_message=f"You are the Senior Admin & Operations Support Specialist. {CONSISTENT_STYLE_GUIDE}"
    )

    compliance_agent = AssistantAgent(
        name="Compliance_Support",
        model_client=model_client,
        description="Specialist for Compliance, data privacy, GDPR, security audits, regulatory rules, and legal policies.",
        system_message=f"You are the Senior Compliance & Risk Support Specialist. {CONSISTENT_STYLE_GUIDE}"
    )

    # Custom Selector Prompt to enforce Manager -> Specialist handoff
    selector_prompt = """You are coordinating a customer support team.
Roles:
{roles}

Conversation history:
{history}

Rules:
1. If Support_Manager has NOT spoken yet, ALWAYS select Support_Manager first to triage the query.
2. After Support_Manager assigns the domain, select ONLY the corresponding specialist from {participants} (AI_Support, Finance_Support, HR_Support, Admin_Support, or Compliance_Support).
3. Never select the same agent twice in a row.

Select the next speaker name only."""

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=4)

    team = SelectorGroupChat(
        participants=[manager, ai_agent, finance_agent, hr_agent, admin_agent, compliance_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt
    )

    result = await team.run(task=user_query)
    await model_client.close()

    routing_note = ""
    assigned_agent = "General Support"
    final_answer = ""

    for msg in result.messages:
        if msg.source == "Support_Manager":
            routing_note = msg.content
        elif msg.source in ["AI_Support", "Finance_Support", "HR_Support", "Admin_Support", "Compliance_Support"]:
            assigned_agent = msg.source.replace("_", " ")
            final_answer = msg.content.replace("TERMINATE", "").strip()

    return routing_note, assigned_agent, final_answer

# Display Existing Chat Messages
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["query"])
    with st.chat_message("assistant"):
        st.caption(f"🧭 **Manager Routing:** {chat['routing']}  |  🏷️ **Handled by:** `{chat['agent']}`")
        st.markdown(f'<div class="response-card">{chat["answer"]}</div>', unsafe_allow_html=True)

# Chat Input Box (Supports pressing Enter natively)
user_prompt = st.chat_input("Ask a question across AI, Finance, HR, Admin, or Compliance...")

if user_prompt:
    if not api_key_present:
        st.error("⚠️ Please configure your `OPENAI_API_KEY` in the `.env` file first.")
    else:
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("👔 Support Manager is analyzing and routing your query..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    routing_note, assigned_agent, final_answer = loop.run_until_complete(
                        route_and_answer_query(user_prompt)
                    )

                    st.caption(f"🧭 **Manager Routing:** {routing_note}  |  🏷️ **Handled by:** `{assigned_agent}`")
                    st.markdown(f'<div class="response-card">{final_answer}</div>', unsafe_allow_html=True)

                    st.session_state.chat_history.append({
                        "query": user_prompt,
                        "routing": routing_note,
                        "agent": assigned_agent,
                        "answer": final_answer
                    })

                except Exception as e:
                    st.error(f"❌ Error processing request: {e}")