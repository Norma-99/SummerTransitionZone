import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv("../.env")

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint="https://summer-openai-c20b7.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)

SYSTEM_PROMPT = "You are a helpful triathlon coach. Use tools when needed."

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"{city}: 22°C, sunny, light wind"

@tool
def adjust_session_for_weather(session: str, weather: str) -> str:
    """Adjust a training session description based on weather conditions."""
    adjustment_prompt = ChatPromptTemplate.from_template(
        "You are a triathlon coach. Rewrite this session for the weather below.\n\n"
        "Weather: {weather}\n\n"
        "Session: {session}"
    )
    chain = adjustment_prompt | llm | StrOutputParser()
    return chain.invoke({"session": session, "weather": weather})

agent = create_agent(llm, [get_weather, adjust_session_for_weather], system_prompt=SYSTEM_PROMPT)

if __name__ == "__main__":
    result = agent.invoke({"messages": [("human", "Should I run outside in Amsterdam today?")]})
    print(result["messages"][-1].content)