# Day 8 — "The Agent Arrives"

**Concept:** LangChain agents · Tool use · ReAct pattern
**You build:** An agent with two tools — one that looks up current weather (fake it with a function) and one that adjusts a training session based on the weather.

---

## The Goal

Days 7 was about a deterministic chain: one prompt goes in, one formatted response comes out. A chain is predictable because the flow is fixed. An agent is different: it can decide at runtime which tool to call, when to call it, and how to combine the results into a final answer.

That is the core idea behind the ReAct pattern: the model thinks, chooses a tool, observes the result, and then responds.

```
User question
   ↓
Agent (decides what to do)
   ├─ tool: get_weather()
   ├─ tool: adjust_session_for_weather()
   └─ final answer
```

---

## Step 0 — Confirm your prior resources are ready

No new Azure resource is needed today — you're reusing the same Azure OpenAI deployment from Day 2.

- [X] Confirm the deployment is still there: `az cognitiveservices account deployment show --name summer-openai --resource-group summer-rg --deployment-name gpt-4o-mini --query "properties.provisioningState" -o tsv` → should print `Succeeded`
- [X] Confirm your `.env` file at the project root still has `AZURE_OPENAI_KEY` set

---

## Step 1 — Install dependencies

- [X] Add to `day8/requirements.txt`:

```
python-dotenv
langchain
langchain-openai
langchain-core
```

- [ ] Install:

```bash
cd day8
pip3.11 install -r requirements.txt
```

---

## Step 2 — Write `main.py`

- [X] Create `day8/main.py`:

```python
mport os
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
```

---

## Step 3 — Run it

- [X] Run from inside `day8/`:

```bash
cd day8
python main.py
```

Expected output shape:

```
It is probably a good day for an outdoor run in Amsterdam...
```

The exact wording will vary, but the important part is that the agent should:

- call the weather tool first
- use the weather result when deciding whether to suggest an outdoor session
- produce a final coaching answer rather than just repeat the raw tool output

---

## Step 4 — Verify

- [X] The agent returns a sensible answer rather than an error
- [X] The agent used the weather tool to inform the recommendation
- [X] The agent combined multiple steps into one response, which is the difference between a chain and an agent
- [X] `grep -r "sk-" day8/` returns nothing — the key still comes from `.env`, not hardcoded

---

## Mental Model

```
User asks: "Should I run outside in Amsterdam today?"
        │
        ▼
Agent decides: I need weather info first
        │
        ▼
get_weather("Amsterdam")
        │
        ▼
Agent uses that result to decide on a training recommendation
        │
        ▼
adjust_session_for_weather(...)
        │
        ▼
Final answer: "Yes, a sunny run is a good idea..."
```

The difference is that a chain has a fixed path. An agent can decide what to do next based on the conversation and available tools. That flexibility is what makes agents useful for more complex workflows.
