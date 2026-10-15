
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load the .env file from the same folder as this script
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Check whether the API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY is missing. Please check your .env file."
    )

# Initialize the LangChain model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# Prompt for exactly five healthy breakfast ideas
prompt = """
Suggest exactly 5 healthy breakfast ideas.

Define healthy as a balanced meal containing nutritious
ingredients, fibre, and a source of protein where practical.

Requirements:
- Number the ideas from 1 to 5.
- Write one line per idea.
- No introduction or conclusion.
- Use practical, easy-to-find ingredients.
- Avoid excessive added sugar and highly processed ingredients.
"""

# Get the model response
reply = llm.invoke(prompt)

# Print only the response text
print(reply.content)