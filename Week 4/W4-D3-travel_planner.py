from crewai import Agent, Task, Crew

city = input("Which city? ")

# Create the Travel Planner Agent
planner = Agent(
    role="Expert Travel Planner",
    goal="Discover and suggest the 3 absolute best places to visit in {city}.",
    backstory=(
        "You are a seasoned global travel curator with a passion for uncovering "
        "both iconic landmarks and hidden gems. You write concise, inspiring recommendations "
        "tailored for curious travelers looking for an unforgettable trip."
    ),
    verbose=True
)

# Create the Task
task = Task(
    description=(
        f"Recommend exactly 3 must-visit places in {city}. "
        "For each place, provide a short title and a 1-sentence description explaining why it's worth visiting."
    ),
    expected_output=(
        "A numbered list of exactly 3 places in the city, with each entry containing a name "
        "and a brief 1-sentence description."
    ),
    agent=planner
)

# Assemble the Crew and Run
crew = Crew(
    agents=[planner],
    tasks=[task],
    verbose=True
)

result = crew.kickoff(inputs={"city": city})
print("\n--- Travel Recommendations ---")
print(result)