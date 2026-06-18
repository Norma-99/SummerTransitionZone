# Deployment Options for AI Apps
### Azure · AWS · GCP — When to Use What

> *"Our company wants to deploy a chatbot and we don't have Kubernetes."*
> This guide answers that question across all three clouds.

---

## The Deployment Ladder

Complexity increases as you go down. **Start from the top** — only go lower when you have a specific reason.

```
Level 1  →  No-code / AI Studio         Zero engineering, business users
Level 2  →  PaaS (App Service)          Push code, no Docker, fastest
Level 3  →  Serverless (Functions)      Event-driven, pay-per-call
Level 4  →  Containers, no cluster      Docker, scales to zero, most flexible
Level 5  →  Kubernetes                  Full control, complex, only when needed
```

---

## Level 1 — No-Code / AI Studio

### What it is
Click-to-deploy LLM apps. No code, no Docker, no servers. Upload your prompt, connect your data, get a URL.

### On Each Cloud

**Azure AI Foundry (was: Azure AI Studio)**
- URL: [ai.azure.com](https://ai.azure.com)
- Build a chatbot with a system prompt + your documents
- Deploy with one click → get a hosted chat UI + an API endpoint
- Integrates with Azure AI Search for RAG (drag and drop)
- Free to use (pay only for underlying OpenAI model calls)

**AWS: Amazon Bedrock + Agents**
- Build agents that call your tools + data sources
- No-code agent builder in the console
- Pay per token only

**GCP: Vertex AI Studio + Agent Builder**
- URL: [console.cloud.google.com/vertex-ai](https://console.cloud.google.com/vertex-ai)
- Similar to Azure AI Foundry
- Gemini Flash free tier makes this almost zero-cost

### AWS equivalent
Bedrock Console → Agents

### GCP equivalent
Vertex AI Agent Builder / AI Studio

### Free tier
✅ Pay for model calls only. Gemini Flash on GCP is effectively free for low usage.

### When to use
- Non-technical team wants a chatbot over company documents
- You need a working demo in 30 minutes
- Prototype before writing any code
- Internal tools where UX doesn't matter

### When NOT to use
- You need custom business logic (validation, calculations, side effects)
- You need full control over the UX
- You're building something users will pay for

### Deploy in 5 minutes (Azure)
1. Go to [ai.azure.com](https://ai.azure.com)
2. Create a project
3. Go to "Deployments" → deploy a model
4. Go to "Playground" → set your system prompt
5. Click "Deploy to web app"

---

## Level 2 — PaaS Web App (App Service / Elastic Beanstalk / App Engine)

### What it is
Push your Python code. The cloud installs your dependencies and runs it. No Docker, no containers, no cluster.

### On Each Cloud

| | Azure | AWS | GCP |
|---|---|---|---|
| **Service** | App Service | Elastic Beanstalk | App Engine |
| **Free tier** | F1: 60 CPU-min/day, 1GB RAM | Free (pay for EC2 underneath, t2.micro free 12mo) | F1: 28 instance-hours/day |
| **Deploy command** | `az webapp up` | `eb deploy` | `gcloud app deploy` |
| **Languages** | Python, Node, .NET, Java, Ruby, PHP | Python, Node, .NET, Java, Ruby, Go, PHP | Python, Node, Java, Go, PHP, Ruby |

### Azure App Service — detailed

```bash
# One command from your project folder:
az webapp up \
  --name my-chatbot \
  --resource-group my-rg \
  --runtime PYTHON:3.11 \
  --sku FREE

# Azure detects requirements.txt, installs deps, runs:
# gunicorn app:app  (Flask/FastAPI)
# or: streamlit run app.py (if you set the startup command)
```

**For Streamlit specifically**, set the startup command:
```bash
az webapp config set \
  --name my-chatbot \
  --resource-group my-rg \
  --startup-file "streamlit run app.py --server.port 8000 --server.address 0.0.0.0"
```

**Limitations of F1 free tier:**
- 60 CPU minutes per day (resets at midnight)
- No custom domain (only `*.azurewebsites.net`)
- No SSL certificate for custom domain
- Shared infrastructure (noisy neighbours)
- Fine for learning, demos, low-traffic tools

**When to upgrade to B1 (~$13/month):**
- Production chatbot with real users
- Need always-on (F1 can go to sleep)
- Need more than 60 CPU minutes/day

### When to use App Service / Elastic Beanstalk / App Engine
- You have a Python/Node web app (Flask, FastAPI, Streamlit)
- You don't want to learn Docker
- You want the simplest possible path to a live URL
- The app is simple (single process, no special system dependencies)

### When NOT to use
- You need multiple services talking to each other
- You have unusual system dependencies (specific C libraries, GPU, etc.)
- You need scale-to-zero (App Service doesn't do this on free/basic tier)
- You need to run background workers separately from the web server

### Real chatbot example
```
User → azurewebsites.net → App Service (Streamlit) → Azure OpenAI → Response
```
This is the simplest possible chatbot architecture. Three boxes. Zero Kubernetes.

---

## Level 3 — Serverless Functions (Azure Functions / Lambda / Cloud Functions)

### What it is
Write individual functions. Each function handles one type of event (HTTP request, file upload, timer, queue message). You pay only when code actually runs.

### On Each Cloud

| | Azure | AWS | GCP |
|---|---|---|---|
| **Service** | Azure Functions | AWS Lambda | Cloud Functions (Gen 2) |
| **Free tier** | ✅ 1M executions/month | ✅ 1M requests/month | ✅ 2M invocations/month 🏆 |
| **Max runtime** | 10 min (Consumption) | 15 min | 60 min |
| **Cold start** | ~1-3s (Python) | ~1-3s (Python) | ~1-3s (Python) |
| **Deploy** | `func azure functionapp publish` | `sam deploy` or `aws lambda update` | `gcloud functions deploy` |

### Azure Functions — detailed

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Create new function project
func init my-chatbot-api --python
cd my-chatbot-api
func new --name Chat --template "HTTP trigger"

# Test locally
func start

# Deploy
az functionapp create \
  --name my-chat-func \
  --resource-group my-rg \
  --consumption-plan-location westeurope \
  --runtime python \
  --runtime-version 3.11 \
  --storage-account mystorageacct

func azure functionapp publish my-chat-func
```

```python
# function_app.py
import azure.functions as func
import json
from openai import AzureOpenAI

app = func.FunctionApp()

@app.route(route="chat", methods=["POST"])
def chat(req: func.HttpRequest) -> func.HttpResponse:
    body     = req.get_json()
    question = body.get("question", "")

    client   = AzureOpenAI(...)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}]
    )
    answer = response.choices[0].message.content
    return func.HttpResponse(json.dumps({"answer": answer}), mimetype="application/json")
```

### When to use Functions / Lambda / Cloud Functions
- You have **an API endpoint**, not a full web app
- Chatbot **webhook** (Slack bot, Teams bot, WhatsApp bot) — these call a URL, a function is perfect
- **Batch processing**: process 100 documents overnight — queue them, function processes each one
- Event-triggered tasks: "when a file is uploaded to Blob → process it → store result"
- **Low and spiky traffic**: you pay nothing when nothing happens
- Cost matters: you pay per-call, not per-hour

### When NOT to use
- You have a full web UI (use App Service or Container Apps instead)
- Long-running jobs > 10 minutes (use Container Apps with jobs, or AKS)
- You need to maintain state between calls (Functions are stateless — use Durable Functions for stateful workflows)
- You want to keep server costs down for consistently high traffic (at high volume, always-on is cheaper)

### Chatbot architectures with Functions

**Teams/Slack bot:**
```
Slack → POST to Function URL → Function calls OpenAI → Returns response → Slack shows it
```

**Async document processing:**
```
User uploads PDF → Blob Storage → triggers Function → Function extracts text + calls AI → 
Result stored → UI polls for result
```

---

## Level 4 — Containers Without a Cluster

### What it is
Package your app in Docker. Run it without managing Kubernetes. The cloud handles scaling, load balancing, and infrastructure. **This is the sweet spot for production AI apps.**

### On Each Cloud

| | Azure | AWS | GCP |
|---|---|---|---|
| **Service** | Container Apps | App Runner | Cloud Run |
| **Free tier** | ✅ 180K vCPU-sec/month | ❌ ($0.064/vCPU-hour) | ✅ 2M requests + 360K GB-sec/month 🏆 |
| **Scale to zero** | ✅ | ✅ | ✅ |
| **Deploy from source** | ✅ `az containerapp up --source .` | ✅ | ✅ `gcloud run deploy --source .` |
| **Custom domains** | ✅ | ✅ | ✅ |
| **Min instances** | 0 (free when idle) or 1 (always warm) | 1 minimum | 0 (free when idle) or 1 |

### Azure Container Apps — detailed

```bash
# Create the app (builds Docker image, deploys, gives you a URL)
az containerapp up \
  --name my-ai-app \
  --resource-group my-rg \
  --location westeurope \
  --source .                    # builds from your Dockerfile in current directory
  --target-port 8501            # Streamlit's port
  --ingress external            # publicly accessible

# With environment variables (secrets)
az containerapp up \
  --name my-ai-app \
  --resource-group my-rg \
  --source . \
  --target-port 8501 \
  --ingress external \
  --env-vars \
    AZURE_OPENAI_KEY=secretref:openai-key \
    LANGFUSE_PUBLIC_KEY=secretref:langfuse-pub
```

**Scale to zero:** When nobody is using your app, it scales down to 0 instances. You pay nothing. When someone opens it, it scales back up (~5s cold start). For a personal tool or low-traffic app, this is ideal.

**Minimum 1 instance:** If you need instant responses (no cold start), set `--min-replicas 1`. Costs ~$5-10/month.

### GCP Cloud Run — detailed

```bash
# Deploy from source (no Dockerfile needed — uses buildpacks)
gcloud run deploy my-ai-app \
  --source . \
  --region europe-west4 \
  --allow-unauthenticated \
  --port 8501

# With env vars
gcloud run deploy my-ai-app \
  --source . \
  --region europe-west4 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_KEY=your-key
```

### When to use Container Apps / App Runner / Cloud Run
- You have a Docker container (any language, any dependencies)
- You want **scale to zero** (pay nothing when idle)
- Your app needs specific system dependencies (GPU libraries, ffmpeg, etc.)
- You're building a **production AI app** that needs to be reliable and scalable
- You want to keep costs low at low traffic

### When NOT to use
- You don't have Docker set up (use App Service instead)
- You need GPU (use Container Apps with GPU support, or AKS with GPU nodes, or Modal)
- You have 10+ microservices that need to talk to each other (consider AKS/GKE)

### Real chatbot architecture with Container Apps

```
GitHub push → GitHub Actions → build Docker image →
push to ghcr.io → Container Apps pulls new image →
rolling deploy → new version live
```

Total infra cost: **€0/month** (free tier) while you're learning.

---

## Level 5 — Kubernetes (AKS / EKS / GKE)

### What it is
Full container orchestration. You manage: pods, deployments, services, ingress, namespaces, node pools, cluster autoscaler...

### On Each Cloud

| | Azure | AWS | GCP |
|---|---|---|---|
| **Service** | AKS | EKS | GKE |
| **Free tier** | ✅ Free cluster management (pay for nodes) | ❌ $0.10/hr per cluster | ✅ 1 free zonal cluster |
| **Managed control plane** | ✅ | ✅ | ✅ |
| **GPU support** | ✅ | ✅ | ✅ |
| **Cheapest cluster** | ~$30/month (1 × B2s node) | ~$73/month ($0.10/hr + node) | ~$30/month (1 × e2-standard-2) |

### When to use Kubernetes
- You have **multiple services** that need to discover and talk to each other
- You need **GPU nodes** for running models locally (CUDA workloads)
- You need **fine-grained resource control** (CPU/memory limits per service)
- You're running something **at scale** (hundreds of concurrent users)
- Your company already has a Kubernetes cluster and you're deploying onto it

### When NOT to use for a chatbot
Almost never, unless:
- The chatbot is part of a larger platform already running on Kubernetes
- You need to run the LLM model yourself (not via API)
- You need very specific networking or security controls

---

## Deployment Decision Tree

```
Do you have a full web UI (Streamlit, FastAPI, React)?
│
├── No (it's just an API endpoint or webhook)
│   └── Use Azure Functions / Lambda / Cloud Functions (Level 3)
│
└── Yes
    │
    ├── Do you want zero Docker / maximum simplicity?
    │   └── Use App Service / Elastic Beanstalk / App Engine (Level 2)
    │
    ├── Do you want "deploy a container, cloud handles the rest"?
    │   └── Use Container Apps / Cloud Run (Level 4) ← recommended for most AI apps
    │
    ├── Do you need no-code / non-technical deploy?
    │   └── Use Azure AI Foundry / Vertex AI Studio (Level 1)
    │
    └── Do you have 10+ services, GPU, or very specific requirements?
        └── Use AKS / GKE / EKS (Level 5)
```

---

## Completely Free Deployment Options (No Azure Credits Needed)

If you want to deploy for **literally €0**, these work:

| Service | What it hosts | Free tier | Notes |
|---|---|---|---|
| **Streamlit Community Cloud** | Streamlit apps | ✅ Unlimited public apps | Deploy from GitHub in 2 clicks. Zero config. Perfect for Streamlit. |
| **Hugging Face Spaces** | Gradio or Streamlit | ✅ Free CPU spaces | Great for ML demos. GPU spaces cost money. |
| **Render** | Any Docker or web app | ✅ Free (sleeps after 15 min) | Wakes up slowly (cold start ~30s). Fine for demos. |
| **Railway** | Any Docker or web app | ✅ $5/month free credit | Easiest experience after Streamlit Cloud. |
| **Fly.io** | Docker containers | ✅ 3 shared VMs free | Global deployment. Good for APIs. |
| **Google Cloud Run** | Docker containers | ✅ 2M requests/month | Best free serverless containers outside Azure. |
| **Vercel** | Next.js, static, APIs | ✅ Generous free tier | Best for frontend + lightweight API routes |

### My recommendation for the Azure Summer project
- **Learning Azure**: use Azure services (the $200 credit + free tiers cover everything)
- **Sharing a demo with someone**: use Streamlit Community Cloud (zero setup, just push to GitHub)
- **Portfolio project after the summer**: deploy on Azure Container Apps (shows Azure skills) + add a Streamlit Cloud version as backup

---

## Deployment Comparison Summary

| | Best for | Free? | Docker needed? | AWS equivalent | GCP equivalent |
|---|---|---|---|---|---|
| **Azure AI Foundry** | Non-technical teams, fast demos | ✅ (model costs only) | ❌ | Bedrock console | Vertex AI Studio |
| **App Service** | Python/Node web apps, no Docker | ✅ F1 tier | ❌ | Elastic Beanstalk | App Engine |
| **Azure Functions** | APIs, webhooks, event processing | ✅ 1M calls/month | ❌ | Lambda | Cloud Functions |
| **Container Apps** | Any Docker app, production chatbots | ✅ 180K vCPU-sec | ✅ | App Runner | Cloud Run |
| **AKS** | Multi-service, GPU, high scale | ✅ (pay for nodes) | ✅ | EKS | GKE |
| **Streamlit Cloud** | Streamlit apps, demos | ✅ Free | ❌ | — | — |
