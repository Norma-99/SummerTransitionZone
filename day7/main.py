import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv("../.env")

# --- The model: same deployment as Day 2, wrapped in LangChain's interface ---
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint="https://summer-openai-c20b7.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)

# --- The prompt: a template with placeholders, not a hardcoded string ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a triathlon coach. Return structured training sessions."),
    ("human", "Create a {duration} minute {sport} session for {fitness_level} level.")
])

# --- The chain: prompt output feeds into the model, model output feeds into the parser ---
chain = prompt | llm | StrOutputParser()


if __name__ == "__main__":
    result = chain.invoke({
        "sport": "run",
        "duration": 45,
        "fitness_level": "beginner"
    })
    print(result)

    # A second chain, reusing the same llm — proves the pieces are composable
    nutrition_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a sports nutritionist. Keep answers to 3 bullet points."),
        ("human", "What should I eat before a {duration} minute {sport} session?")
    ])
    nutrition_chain = nutrition_prompt | llm | StrOutputParser()

    print("\n--- Nutrition chain ---")
    print(nutrition_chain.invoke({"sport": "run", "duration": 45}))