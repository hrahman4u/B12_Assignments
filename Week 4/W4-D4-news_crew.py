import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load environment variables from the .env file
load_dotenv()

# Verify keys are loaded (optional check)
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables or .env file.")

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

result = crew.kickoff()
print("\n--- Final Newsletter Output ---")
print(result)