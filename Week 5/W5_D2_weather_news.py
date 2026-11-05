import asyncio
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

def search_weather_news(city: str) -> str:
    """Search the web for today's weather news in the specified city."""
    return str(DDGS().news(query=f"{city} weather today", max_results=5))

city = input("Which city? ")
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

agent = AssistantAgent(
    name="weather_news",
    model_client=model_client,
    tools=[search_weather_news],
    system_message=(
        "You are a helpful weather news assistant. "
        "When given a city, use the search tool to find today's weather news "
        "and reply in exactly 3 short lines."
    ),
    reflect_on_tool_use=True
)

async def main():
    await Console(agent.run_stream(task=f"Give me today's weather news for {city}."))
    await model_client.close()

asyncio.run(main())