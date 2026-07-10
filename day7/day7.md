# Day 7 — "The Chain Gang"

**Concept:** LangChain basics · LCEL · `ChatPromptTemplate` · Chains
**You build:** A structured training session generator — input sport + duration + fitness level → get a formatted session plan back, using LangChain instead of calling the OpenAI SDK directly.

---

## The Goal

Days 2–6 called `AzureOpenAI` directly: build a `messages` list by hand, call `.chat.completions.create()`, read `.choices[0].message.content`. That works, but it doesn't scale — every new prompt means rewriting that boilerplate.

LangChain's answer is **LCEL** (LangChain Expression Language): you build small, reusable pieces — a prompt template, a model, an output parser — and glue them together with the `|` (pipe) operator into a **chain**. No new Azure resources today; you're reusing the `summer-openai` deployment from Day 2, just calling it through a different library.

```
ChatPromptTemplate  |  AzureChatOpenAI  |  StrOutputParser
     (fills in the prompt)   (calls the model)   (extracts plain text)
```

---

## Step 0 — Confirm your prior resources are ready

No new resources today — you're reusing Day 2's deployment.

- [X] Confirm the deployment is still there: `az cognitiveservices account deployment show --name summer-openai --resource-group summer-rg --deployment-name gpt-4o-mini --query "properties.provisioningState" -o tsv` → should print `Succeeded`
- [X] Confirm your `.env` (at the project root) still has `AZURE_OPENAI_KEY` set

---

## Step 1 — Install dependencies

- [X] Add to `day7/requirements.txt`:

```
python-dotenv
langchain
langchain-openai
langchain-core
```

- [ ] Install:

```bash
cd day7
pip3.11 install -r requirements.txt
```

---

## Step 2 — Write `main.py`

- [X] Create `day7/main.py`:

```python
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
        "fitness_level": "intermediate"
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
```

---

## Step 3 — Run it

- [X] Run from inside `day7/`:

```bash
cd day7
python main.py
```

Expected output shape:

```
Warm-up: 10 min easy jog...
Main set: ...
Cool-down: ...

--- Nutrition chain ---
- Eat a carb-rich snack 1-2 hours before...
- ...
```

---

## Step 4 — Verify

- [X] The first chain's output is a coherent training session (not an error, not empty)
- [X] The second chain's output is a nutrition answer — proves `llm` was reused across two different `prompt | llm | parser` chains without modification
- [X] Change `fitness_level` to `"beginner"` and re-run — the output should noticeably change (shorter/easier session), confirming the template variables are actually wired in
- [X] `grep -r "sk-" day7/` returns nothing — the key still comes from `.env`, not hardcoded

---

## Mental Model

```
{"sport": "run", "duration": 45, "fitness_level": "intermediate"}
        │
        ▼
ChatPromptTemplate.from_messages([...])   → fills placeholders → list of messages
        │  |
        ▼
AzureChatOpenAI(...)                       → sends messages to gpt-4o-mini → AIMessage
        │  |
        ▼
StrOutputParser()                          → extracts just the text content
        │
        ▼
"Warm-up: ... Main set: ... Cool-down: ..."
```

The `|` operator isn't magic — each piece implements the same `Runnable` interface (`.invoke()`, `.batch()`, `.stream()`), so LangChain can pipe the output of one directly into the input of the next. That's the whole idea behind LCEL: build once, then recombine the same small pieces (`llm`, parsers, prompts) into as many different chains as you need.

---
