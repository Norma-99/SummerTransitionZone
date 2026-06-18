# ☀️ Summer Transition Zone
A summer wordbook dedicated to learn Azure in the AI / LLM realm

### 20 Days of Azure, LangChain & AI 

> One challenge per session. Each one takes ~2 hours. Each one teaches one thing.
> By Day 20 you'll have touched every Azure service that matters for AI work — and built things you can show.

**Schedule:** 2–3 sessions per week · 8 weeks · ~40 hours total
**Format:** Each day = one concept + one thing you build + one "done when" check

---

## How This Works

Each challenge is self-contained. You don't need to finish Day 3 before starting Day 4 (though the early ones do build on each other). Every day ends with something deployed or running — not just notes.

Difficulty increases gradually:
```
Weeks 1–2  →  Azure foundations  (setup, deploy, storage)
Weeks 3–4  →  LangChain + RAG    (chains, agents, search)
Weeks 5–6  →  LangGraph + Observability  (multi-agent, tracing)
Weeks 7–8  →  Advanced + Capstone  (serverless, CI/CD, your project)
```

---

## WEEK 1 — Hello, Azure

### Day 1 — "Flip the Switch"
**Concept:** Azure account setup · Resource groups · Azure CLI · First deployment
**You build:** A static "Hello, I'm learning Azure" webpage live on the internet in under 10 minutes.

```bash
# After signup at portal.azure.com
az login
az group create --name summer-rg --location westeurope
az staticwebapp create --name my-first-azure-app --resource-group summer-rg
```

**Study (30 min before building):**
- [Azure for AWS Professionals — Overview section](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/) — understand Resource Groups (they're not like anything in AWS; think "folder for billing + permissions")
- [AWS → Azure Cheat Sheet](https://tutorialsdojo.com/aws-vs-azure-services-comparison/) — bookmark this, you'll use it every week

**✅ Done when:** You have a live URL with your page on it. Takes 10 minutes. Spend the rest of the session reading the AWS→Azure docs.

---

### Day 2 — "Ask the Machine"
**Concept:** Azure OpenAI Service · API keys · First model call from Python
**You build:** A Python script that asks GPT-4o-mini a question and prints the answer.

```bash
az cognitiveservices account create \
  --name summer-openai --resource-group summer-rg \
  --kind OpenAI --sku S0 --location swedencentral

az cognitiveservices account deployment create \
  --name summer-openai --resource-group summer-rg \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini --model-version "2024-07-18" \
  --model-format OpenAI --sku-name Standard
```

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="...",
    api_version="2024-02-01",
    azure_endpoint="https://summer-openai.openai.azure.com/"
)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain Azure in one sentence."}]
)
print(response.choices[0].message.content)
```

**Study (30 min):**
- [Azure OpenAI quickstart — Python](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line&pivots=programming-language-python)

**✅ Done when:** Python script runs, prints a real AI response, you understand what `azure_endpoint` and `api_version` are and why they exist.

---

### Day 3 — "Easiest Chatbot Deploy Ever"
**Concept:** Azure App Service · Deploying a Python web app without Docker
**You build:** A Streamlit chatbot with memory, deployed publicly via App Service.

This is the answer to "how does a company deploy a chatbot without Kubernetes." It's literally one command:

```bash
# In your project folder with app.py
az webapp up \
  --name summer-chatbot \
  --resource-group summer-rg \
  --runtime PYTHON:3.11 \
  --sku FREE
```

That's it. Azure reads your `requirements.txt`, installs deps, and serves it.

**What to build:**
```python
# app.py — simple Streamlit chatbot
import streamlit as st
from openai import AzureOpenAI

client = AzureOpenAI(...)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Say something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
```

**Study (30 min):**
- [Azure App Service overview](https://learn.microsoft.com/en-us/azure/app-service/overview)
- [John Savill — App Service module](https://www.youtube.com/@NTFAQGuy) (search "App Service" on his channel, ~20 min)

**✅ Done when:** Your chatbot is live at `https://summer-chatbot.azurewebsites.net` and you can talk to it from your phone.

---

## WEEK 2 — Storage & Secrets

### Day 4 — "The File Cabinet"
**Concept:** Azure Blob Storage · Upload · Download · Public URLs
**You build:** A Python script that uploads a training log CSV, reads it back, and lists all files in a container.

```python
from azure.storage.blob import BlobServiceClient

client = BlobServiceClient.from_connection_string("...")
container = client.get_container_client("training-logs")
container.create_container()

# Upload
with open("garmin_export.csv", "rb") as f:
    container.upload_blob("garmin_export.csv", f)

# List
for blob in container.list_blobs():
    print(blob.name)

# Download
data = container.download_blob("garmin_export.csv").readall()
```

**Study (30 min):**
- [Azure Blob Storage quickstart — Python](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)
- Key concept: Blob Storage = S3. Container = S3 bucket. Blob = S3 object. Same idea, different API.

**✅ Done when:** You can upload a file, list it, download it. You understand the relationship: Storage Account → Container → Blob.

---

### Day 5 — "No Keys Under the Mat"
**Concept:** Azure Key Vault · Managed Identity · Secret management without `.env` files
**You build:** Your Day 3 chatbot, but now it reads secrets from Key Vault instead of environment variables — and uses Managed Identity (no credentials at all in code).

```bash
# Create Key Vault
az keyvault create --name summer-kv --resource-group summer-rg --location westeurope

# Store your OpenAI key
az keyvault secret set --vault-name summer-kv --name openai-key --value "sk-..."

# Enable managed identity on your App Service
az webapp identity assign --name summer-chatbot --resource-group summer-rg

# Grant access
az keyvault set-policy --name summer-kv \
  --object-id <identity-id> \
  --secret-permissions get list
```

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://summer-kv.vault.azure.net/", credential=credential)
openai_key = client.get_secret("openai-key").value
```

**Study (30 min):**
- [Key Vault quickstart](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python)
- [Managed Identity explained](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) — this is the "no API key in code ever" pattern. Important concept for production work.

**✅ Done when:** Your app has no secrets in code or `.env`. It uses Managed Identity to fetch secrets from Key Vault at runtime.

---

### Day 6 — "Read the Document"
**Concept:** Combining Blob Storage + Azure OpenAI · Building your first useful AI tool
**You build:** Upload a PDF to Blob Storage → extract text → summarise with AI → return a bullet-point summary.

```python
import fitz   # PyMuPDF — for PDF text extraction

def summarise_document(blob_name: str) -> str:
    # 1. Download from Blob
    pdf_bytes = container.download_blob(blob_name).readall()

    # 2. Extract text
    doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)

    # 3. Summarise with AI
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarise this document in 5 bullet points."},
            {"role": "user",   "content": text[:8000]}   # token limit safety
        ]
    )
    return response.choices[0].message.content
```

**✅ Done when:** You upload a real PDF (e.g. a training plan, a race guide), call the function, get a clean summary back.

---

## WEEK 3 — LangChain

### Day 7 — "The Chain Gang"
**Concept:** LangChain basics · LCEL · ChatPromptTemplate · Chains
**You build:** A structured training session generator — input sport + duration → get a formatted session plan back.

```python
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = AzureChatOpenAI(azure_deployment="gpt-4o-mini", ...)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a triathlon coach. Return structured training sessions."),
    ("human", "Create a {duration} minute {sport} session for {fitness_level} level.")
])

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "sport": "run",
    "duration": 45,
    "fitness_level": "intermediate"
})
print(result)
```

**Study (1h):**
- [LangChain LCEL Quickstart](https://python.langchain.com/docs/tutorials/llm_chain/) — the `prompt | llm | parser` pattern is the core concept. Spend time here.
- [LangChain + Azure OpenAI](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

**✅ Done when:** You understand why `|` works (it's the pipe operator for LCEL) and you've built at least two different chains with different prompts.

---

### Day 8 — "The Agent Arrives"
**Concept:** LangChain agents · Tool use · ReAct pattern
**You build:** An agent with two tools — one that looks up current weather (fake it with a function) and one that adjusts a training session based on the weather.

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Amsterdam: 22°C, sunny, light wind"  # mock — replace with real API

@tool
def adjust_session_for_weather(session: str, weather: str) -> str:
    """Adjust a training session description based on weather conditions."""
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"session": session, "weather": weather})

agent = create_tool_calling_agent(llm, [get_weather, adjust_session_for_weather], prompt)
executor = AgentExecutor(agent=agent, tools=[get_weather, adjust_session_for_weather])
result = executor.invoke({"input": "Should I run outside in Amsterdam today?"})
```

**Study (30 min):**
- [LangChain agents quickstart](https://python.langchain.com/docs/tutorials/agents/)

**✅ Done when:** The agent calls your tools in the right order and returns a sensible answer. You understand the difference between a chain (deterministic) and an agent (decides what to call at runtime).

---

### Day 9 — "Ask the Library"
**Concept:** RAG (Retrieval-Augmented Generation) · Text splitting · Vector embeddings · Local vectorstore
**You build:** A Q&A bot over a local document (e.g. a race guide or training plan PDF). Ask it questions, it finds the relevant section and answers.

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA

# Load + chunk
loader   = PyPDFLoader("race_guide.pdf")
docs     = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks   = splitter.split_documents(docs)

# Embed + store (locally — no Azure service needed today)
embeddings  = AzureOpenAIEmbeddings(azure_deployment="text-embedding-3-small", ...)
vectorstore = FAISS.from_documents(chunks, embeddings)

# Query
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
print(qa.invoke("What time does transition 1 close?"))
```

**Study (45 min):**
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- Key concept to understand: *why chunking exists* (context window limits) and *why embeddings work* (semantic similarity in vector space)

**✅ Done when:** You can ask a question about your PDF and get a correctly sourced answer. Try a question the model couldn't possibly know without the document.

---

## WEEK 4 — Azure AI Search (RAG at Scale)

### Day 10 — "The Real Search Engine"
**Concept:** Azure AI Search · Indexes · Semantic search · Vector search
**You build:** Replace Day 9's local FAISS store with Azure AI Search — the production-grade version.

```bash
az search service create \
  --name summer-search \
  --resource-group summer-rg \
  --sku free                    # free tier: 50MB, 3 indexes — enough for learning
```

**Study (1h):**
- [Azure AI Search overview](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search)
- [Vector search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)
- Key concept: Azure AI Search = a managed ElasticSearch-like service with native vector search and semantic ranking. This is what you'd use instead of Pinecone or FAISS in production.

**✅ Done when:** You've created an index, ingested some documents, and run a semantic query in the Azure portal. You understand what an "index schema" is.

---

### Day 11 — "The Expert Assistant"
**Concept:** LangChain + Azure AI Search · Production RAG pipeline
**You build:** Connect Day 9's RAG app to Azure AI Search instead of FAISS. Add source citations to every answer.

```python
from langchain_community.vectorstores import AzureSearch

vectorstore = AzureSearch(
    azure_search_endpoint="https://summer-search.search.windows.net",
    azure_search_key="...",
    index_name="documents",
    embedding_function=embeddings.embed_query,
)

# Now your RAG chain is backed by a real search service
retriever = vectorstore.as_retriever(search_type="similarity", k=4)
```

**✅ Done when:** Your chatbot answers questions, cites which document section it used, and the answers are backed by Azure AI Search (you can verify queries in the portal).

---

## WEEK 5 — LangGraph

### Day 12 — "First Graph"
**Concept:** LangGraph · StateGraph · Nodes · Edges · State
**You build:** A two-node graph. Node 1 classifies the user's question (training / nutrition / race logistics). Node 2 answers it with a sport-specific prompt.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    question: str
    category: str   # filled by node 1
    answer:   str   # filled by node 2

def classify(state: State) -> State:
    result = classifier_chain.invoke({"question": state["question"]})
    state["category"] = result
    return state

def answer(state: State) -> State:
    result = answer_chain.invoke({
        "question": state["question"],
        "category": state["category"]
    })
    state["answer"] = result
    return state

graph = StateGraph(State)
graph.add_node("classify", classify)
graph.add_node("answer",   answer)
graph.set_entry_point("classify")
graph.add_edge("classify", "answer")
graph.add_edge("answer", END)
app = graph.compile()

result = app.invoke({"question": "How long should I taper before a sprint tri?"})
print(result["answer"])
```

**Study (1h):**
- [LangGraph Introduction Tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/) — do the whole thing. ~1h.
- Key concept: LangGraph is a state machine. Each node reads state, modifies it, returns it. Edges decide what runs next.

**✅ Done when:** Graph runs, state is updated at each node, you can print the intermediate state to verify each step worked.

---

### Day 13 — "Multiple Agents, One Goal"
**Concept:** LangGraph · Multiple nodes · Conditional edges · A real multi-agent pipeline
**You build:** A 3-agent training plan generator:
- Agent 1: Analyse the user's current fitness (input: recent activity summary)
- Agent 2: Set weekly training targets
- Agent 3: Generate the day-by-day plan

Add a conditional edge: if Agent 1 detects overtraining, skip Agent 2 and go straight to a "recommend rest week" node.

**Study (30 min):**
- [LangGraph: How to add conditional edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)

**✅ Done when:** The conditional branch works — when you input a high fatigue level, the graph takes the rest-week path instead of the planning path.

---

### Day 14 — "Wait for the Human"
**Concept:** LangGraph Human-in-the-Loop · Interrupts · Approving AI decisions
**You build:** Add a review step to your Day 13 graph. After Agent 2 sets the weekly targets, the graph pauses and asks the user "Does this look right? (y/n)". Only continues if approved.

```python
from langgraph.checkpoint.memory import MemorySaver

# Add interrupt before the plan generation step
graph.add_node("review_targets", review_node)
graph.add_edge("set_targets", "review_targets")
graph.add_conditional_edges("review_targets", human_approved, {
    True:  "generate_plan",
    False: "set_targets"    # loop back, regenerate targets
})

# Compile with checkpointing so state persists across interrupts
memory = MemorySaver()
app = graph.compile(checkpointer=memory, interrupt_before=["review_targets"])
```

**Study (30 min):**
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

**✅ Done when:** The graph pauses, prints the targets, waits for your input, and either regenerates or continues.

---

## WEEK 6 — Observability

### Day 15 — "See Everything"
**Concept:** Langfuse · LLM tracing · Cost tracking · Span inspection
**You build:** Add Langfuse tracing to your Day 13 LangGraph pipeline. After running, inspect the dashboard.

```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://cloud.langfuse.com",
)

# Add to every chain invoke
result = chain.invoke(inputs, config={"callbacks": [handler]})
```

**Sign up:** [langfuse.com](https://langfuse.com) — free cloud tier, no credit card.

**Study (30 min):**
- [Langfuse Python Quickstart](https://langfuse.com/docs/get-started)
- [Langfuse + LangChain integration](https://langfuse.com/docs/integrations/langchain/tracing)

**✅ Done when:** You can see all 3 agent spans in the Langfuse dashboard with latency, cost, and the actual prompts + responses for each one. You can answer: which agent is most expensive?

---

### Day 16 — "Azure's Own Dashboard"
**Concept:** Azure Monitor · Application Insights · Custom metrics
**You build:** Add Application Insights to your Day 3 chatbot. Track: number of questions asked, response latency, errors.

```bash
az monitor app-insights component create \
  --app summer-insights \
  --resource-group summer-rg \
  --location westeurope
```

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient(instrumentation_key="...")
tc.track_event("ChatMessage", {"user_message": prompt, "response_length": len(reply)})
tc.track_metric("ResponseLatency", latency_ms)
```

**Study (30 min):**
- [Application Insights overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- This is your CloudWatch equivalent. Same concept: logs, metrics, traces — different portal.

**✅ Done when:** You can see your custom events in the Azure portal under Application Insights → Events. Set up one alert (e.g. alert if response latency > 5 seconds).

---

## WEEK 7 — Serverless & Container Deployment

### Day 17 — "The Function That Thinks"
**Concept:** Azure Functions · HTTP trigger · Serverless AI
**You build:** An Azure Function that receives a POST request with a training question and returns an AI answer. This is what you'd use for a Teams or Slack bot webhook.

```bash
func init summer-func --python
func new --name AskAI --template "HTTP trigger"
func start   # test locally
func azure functionapp publish summer-func   # deploy
```

```python
# function_app.py
import azure.functions as func

app = func.FunctionApp()

@app.function_name("AskAI")
@app.route(route="ask", methods=["POST"])
def ask_ai(req: func.HttpRequest) -> func.HttpResponse:
    body    = req.get_json()
    question = body.get("question")
    answer  = ai_chain.invoke({"question": question})
    return func.HttpResponse(answer, mimetype="text/plain")
```

**Study (30 min):**
- [Azure Functions Python quickstart](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python)
- Install: `npm install -g azure-functions-core-tools@4`

**✅ Done when:** You send a POST request to your live Azure Function URL and get an AI answer back. Test with `curl` or Postman.

---

### Day 18 — "The Real Deployment"
**Concept:** Azure Container Apps · Docker · GitHub Actions CI/CD
**You build:** Take your Day 13 multi-agent graph, wrap it in a FastAPI app, containerise it, and deploy it with a GitHub Actions pipeline so every push to `main` auto-deploys.

```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure Container Apps
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: az acr build --registry summeracr --image app:${{ github.sha }} .
      - uses: azure/container-apps-deploy-action@v1
        with:
          containerAppName: summer-app
          resourceGroup: summer-rg
          imageToDeploy: summeracr.azurecr.io/app:${{ github.sha }}
```

**Study (30 min):**
- [Container Apps quickstart](https://learn.microsoft.com/en-us/azure/container-apps/get-started)
- [GitHub Actions + Container Apps](https://github.com/Azure/container-apps-deploy-action)

**✅ Done when:** You push a code change, watch GitHub Actions run, and see the new version live 3–4 minutes later. You never manually ran a deploy command.

---

## WEEK 8 — Capstone

### Day 19 — "Your Thing"
**What to build:** A small AI app of your own choosing that uses at least 3 services from the summer.

**Ideas (if you need one):**
- A race day chatbot: upload a race guide PDF to Blob, answer questions about it with RAG + AI Search
- A training week summariser: upload a Garmin export, summarise the week with LangGraph + Langfuse tracing
- A workout Q&A agent: 3-tool LangGraph agent that knows about running, cycling, and swimming

**This session:** Plan it, scaffold the project structure, get the first LLM call working.

---

### Day 20 — "Ship It"
**What to do:** Finish and deploy your Day 19 project. Write a one-paragraph README explaining what it does and why you built it.

This is your portfolio piece. If someone asks what you've been doing with Azure, you show them this.

**Checklist before you're done:**
- [ ] App is deployed and publicly accessible
- [ ] Secrets are in Key Vault or Container Apps env vars — not in code
- [ ] At least one Langfuse trace visible in the dashboard
- [ ] README has: what it does, how to run it, what Azure services it uses

---

## Services Covered — Summary

| Day | Azure Service Learned |
|---|---|
| 1 | Azure CLI, Resource Groups, Static Web Apps |
| 2 | Azure OpenAI Service |
| 3 | Azure App Service ← **easiest chatbot deploy** |
| 4 | Azure Blob Storage |
| 5 | Azure Key Vault, Managed Identity |
| 6 | Blob + OpenAI combined |
| 7–9 | LangChain (chains, agents, RAG) |
| 10–11 | Azure AI Search ← **production RAG** |
| 12–14 | LangGraph (graphs, multi-agent, human-in-the-loop) |
| 15 | Langfuse (LLM observability) |
| 16 | Azure Monitor, Application Insights |
| 17 | Azure Functions ← **serverless chatbot** |
| 18 | Azure Container Apps + GitHub Actions CI/CD |
| 19–20 | Capstone — your choice |

---

## Quick Reference Links

| Topic | Link |
|---|---|
| Azure for AWS Professionals | [learn.microsoft.com/en-us/azure/architecture/aws-professional](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/) |
| AWS → Azure Cheat Sheet | [tutorialsdojo.com/aws-vs-azure-services-comparison](https://tutorialsdojo.com/aws-vs-azure-services-comparison/) |
| John Savill (Azure YouTube) | [youtube.com/@NTFAQGuy](https://www.youtube.com/@NTFAQGuy) |
| LangGraph Tutorial | [langchain-ai.github.io/langgraph/tutorials/introduction](https://langchain-ai.github.io/langgraph/tutorials/introduction/) |
| LangChain Docs | [python.langchain.com](https://python.langchain.com) |
| Langfuse Quickstart | [langfuse.com/docs/get-started](https://langfuse.com/docs/get-started) |
| Azure Functions Python | [learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python) |
| Azure Container Apps | [learn.microsoft.com/en-us/azure/container-apps](https://learn.microsoft.com/en-us/azure/container-apps/) |
| Azure AI Search | [learn.microsoft.com/en-us/azure/search](https://learn.microsoft.com/en-us/azure/search/) |
| Azure App Service | [learn.microsoft.com/en-us/azure/app-service](https://learn.microsoft.com/en-us/azure/app-service/) |
