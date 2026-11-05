import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 1. Initialize the model client (uses OPENAI_API_KEY from your environment variables)
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# 2. Create the AssistantAgent with the exact required system message
agent = AssistantAgent(
    name="hr_assistant",
    model_client=model_client,
    system_message="You are an HR assistant."
)

# 3. Define the async main function to run the agent task
async def main():
    # Ask for a 5-line job description, explicitly specifying bullets/sentences so the model knows the format
    task_prompt = (
        "Write a 5-line job description for a Junior Python Developer. "
        "Provide exactly five bullet points or sentences and nothing more."
    )
    
    # Run the stream through the Console UI
    await Console(agent.run_stream(task=task_prompt))
    
    # Close the model client to prevent the script from hanging
    await model_client.close()

# 4. Execute using asyncio
if __name__ == "__main__":
    asyncio.run(main())