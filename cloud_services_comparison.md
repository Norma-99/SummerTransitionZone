# Cloud Services Comparison
### AWS · Azure · GCP — AI & MLOps Reference Sheet

> Focus: services relevant to AI apps, MLOps, and backend engineering.
> Free tier info current as of mid-2025. Always verify at each provider's pricing page.

---

## How to Read This Sheet

- ✅ **Free tier exists** — meaningful free usage available
- ⚠️ **Tiny free tier** — technically free but too small for real use
- ❌ **No free tier** — pay from first use (credits may cover this)
- 🏆 **Best free tier** — clear winner among the three

---

## 1. Serverless Functions

*Run code without managing servers. Pay per execution.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | Lambda | Azure Functions | Cloud Functions (Gen 2) |
| **Free tier** | ✅ 1M requests + 400K GB-sec/month | ✅ 1M executions + 400K GB-sec/month | ✅ 2M invocations + 400K GB-sec/month 🏆 |
| **Max timeout** | 15 min | 10 min (Consumption), unlimited (Premium) | 60 min |
| **Cold start** | Fast (JS/Python) | Fast | Fast |
| **Trigger types** | HTTP, S3, SQS, EventBridge, many more | HTTP, Blob, Queue, Timer, Event Grid | HTTP, Pub/Sub, Cloud Storage, Firestore |
| **AWS → Azure** | Lambda = Azure Functions | | |
| **AWS → GCP** | Lambda = Cloud Functions | | |
| **AI use case** | Chatbot webhook, batch inference, doc processing |
| **Notes** | Lambda has the richest ecosystem. All three are essentially equivalent for HTTP triggers. GCP has the best free tier. |

---

## 2. Containers Without a Cluster

*Run Docker containers without managing Kubernetes. The "just run my app" option.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | App Runner | Azure Container Apps | Cloud Run |
| **Free tier** | ❌ ($0.064/vCPU-hour) | ✅ 180K vCPU-sec + 360K GB-sec/month | ✅ 2M requests + 360K GB-sec/month 🏆 |
| **Scale to zero** | ✅ | ✅ | ✅ |
| **AWS → Azure** | App Runner ≈ Container Apps (Container Apps is more capable) | | |
| **AWS → GCP** | App Runner ≈ Cloud Run | | |
| **AI use case** | Streamlit apps, FastAPI chatbots, LangGraph services |
| **Notes** | **Cloud Run and Container Apps both have excellent free tiers. AWS App Runner has no free tier.** For learning, Azure or GCP wins here. Cloud Run is slightly more mature; Container Apps has better Azure ecosystem integration. |

> **This is the answer to "deploy a chatbot without Kubernetes."** Package your app in Docker → deploy to Container Apps or Cloud Run → done.

---

## 3. PaaS Web Apps (No Docker Needed)

*Push code, cloud handles the runtime. No Dockerfile required.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | Elastic Beanstalk | App Service | App Engine |
| **Free tier** | ✅ (free — pay for EC2 underneath) | ✅ F1 tier: 60 CPU-min/day, 1GB RAM | ✅ F1 instance: 28 instance-hours/day |
| **Deploy command** | `eb deploy` | `az webapp up` | `gcloud app deploy` |
| **AWS → Azure** | Elastic Beanstalk ≈ App Service | | |
| **AWS → GCP** | Elastic Beanstalk ≈ App Engine | | |
| **AI use case** | Simple chatbots, Streamlit apps, FastAPI |
| **Notes** | App Service is the easiest: `az webapp up` detects your runtime automatically. F1 free tier is limited but enough for demos. App Engine Standard has generous free tier too. |

---

## 4. Kubernetes (Managed)

*Run Kubernetes without managing control plane.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | EKS | AKS | GKE |
| **Free tier** | ❌ $0.10/hr per cluster | ✅ Free cluster management (pay for nodes) | ✅ 1 free zonal cluster per billing account 🏆 |
| **Market share** | 🥇 Largest | 🥈 | 🥉 (but most mature Kubernetes) |
| **AWS → Azure** | EKS = AKS | | |
| **AWS → GCP** | EKS = GKE | | |
| **AI use case** | Large-scale ML inference, multi-service AI platforms, GPU workloads |
| **Notes** | Don't start here for learning. GKE is often considered the most polished (Google invented Kubernetes). AKS is getting much better. EKS has most features for AWS-native workflows. |

---

## 5. Object Storage

*Store files, blobs, datasets, model artifacts.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | S3 | Blob Storage | Cloud Storage |
| **Free tier** | ✅ 5GB (12 months) | ✅ 5GB LRS (12 months) | ✅ 5GB Regional (always free) 🏆 |
| **Concepts** | Bucket → Object | Storage Account → Container → Blob | Bucket → Object |
| **AWS → Azure** | S3 bucket = Blob container | S3 object = Blob | `aws s3 cp` = `az storage blob upload` |
| **AWS → GCP** | S3 bucket = GCS Bucket | S3 object = GCS Object | `aws s3 cp` = `gsutil cp` |
| **AI use case** | Store training data, model artifacts, Garmin CSV exports, generated files |
| **Notes** | All three are functionally identical for most use cases. GCP has always-free 5GB (not just 12 months). Azure requires a "Storage Account" parent resource (no AWS equivalent — just a namespace). |

---

## 6. Relational Database

*PostgreSQL, MySQL, managed by the cloud.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | RDS (PostgreSQL/MySQL) | Azure Database for PostgreSQL | Cloud SQL |
| **Free tier** | ✅ 750h/month, db.t2.micro (12 months) | ✅ 750h/month, Burstable B1ms (12 months) | ❌ ($300 credit covers it) |
| **pgvector support** | ✅ (RDS for PostgreSQL) | ✅ | ✅ |
| **AWS → Azure** | RDS = Azure Database for PostgreSQL | | |
| **AWS → GCP** | RDS = Cloud SQL | | |
| **AI use case** | Store chat history, user profiles, training plans, pgvector for embeddings |
| **Notes** | All three support PostgreSQL with pgvector extension — meaning you can store and query embeddings without a separate vector database. This is often the simplest RAG storage solution. |

---

## 7. NoSQL / Document Database

*Schema-flexible, high-throughput document storage.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | DynamoDB | Cosmos DB | Firestore |
| **Free tier** | ✅ 25GB + 25 WCU/RCU always free 🏆 | ✅ 400 RU/s + 5GB (30 days free trial) | ✅ 1GB + 50K reads/day always free |
| **AWS → Azure** | DynamoDB ≈ Cosmos DB (Table API) | | |
| **AWS → GCP** | DynamoDB ≈ Firestore | | |
| **AI use case** | Store conversation history, session state, user preferences |
| **Notes** | DynamoDB has the best always-free tier. Cosmos DB is more complex but multi-model (document, graph, key-value). Firestore is simplest to get started with. |

---

## 8. Cache

*In-memory key-value store. Fast session storage, rate limiting.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | ElastiCache (Redis/Valkey) | Azure Cache for Redis | Memorystore |
| **Free tier** | ❌ | ❌ (~$13/month for C0 Basic) | ❌ |
| **Cheapest option** | ~$12/month (cache.t2.micro) | ~$13/month (C0) | ~$35/month |
| **AI use case** | LLM response caching, rate limiting, session storage |
| **Free alternative** | 🏆 **Upstash** (upstash.com) — 10,000 commands/day free, Redis-compatible, works with all three clouds |
| **Notes** | None of the three have free managed Redis. Use Upstash for learning and low-traffic apps. |

---

## 9. LLM APIs

*Call foundation models via API.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | Amazon Bedrock | Azure OpenAI Service | Vertex AI / Gemini API |
| **Models available** | Claude, Llama, Mistral, Titan, Nova | GPT-4o, o1, o3-mini, Phi | Gemini Flash/Pro/Ultra, Llama, Claude |
| **Free tier** | ❌ (pay per token) | ❌ (pay per token) | ✅ Gemini Flash: 15 RPM free via AI Studio 🏆 |
| **Cheapest model** | Llama 3 via Bedrock (~free-ish) | GPT-4o-mini ($0.15/1M input tokens) | Gemini 1.5 Flash ($0.075/1M input tokens) |
| **AWS → Azure** | Bedrock ≈ Azure OpenAI Service | | |
| **AWS → GCP** | Bedrock ≈ Vertex AI | | |
| **AI use case** | Everything — this is the core of any AI app |
| **Notes** | **For free learning: GCP Gemini API via Google AI Studio** (aistudio.google.com) — completely free for low usage. For Azure exercises: covered by $200 credit, actual cost is pennies with GPT-4o-mini. |

---

## 10. ML Platform (Training, Experiments, Endpoints)

*Managed platform for training models, tracking experiments, and deploying them.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | SageMaker | Azure Machine Learning | Vertex AI |
| **Free tier** | ⚠️ Some free compute (t2.medium) | ✅ Basic compute + experiment tracking | ⚠️ $300 credit |
| **MLflow support** | ✅ (SageMaker Experiments = MLflow compatible) | ✅ (native MLflow integration) | ✅ (via Vertex AI Experiments) |
| **AWS → Azure** | SageMaker = Azure ML | | |
| **AWS → GCP** | SageMaker = Vertex AI | | |
| **AI use case** | Training custom models, hyperparameter tuning, experiment tracking |
| **Notes** | For MLOps work (your background), Azure ML has the smoothest MLflow integration. All three support model registries and deployment pipelines. |

---

## 11. Vector Search / Search

*Search over text and embeddings. Core of any RAG pipeline.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | OpenSearch Service | Azure AI Search | Vertex AI Vector Search |
| **Free tier** | ❌ (t3.small.search ~$25/month) | ✅ 3 indexes, 50MB, 1 service 🏆 | ❌ |
| **Semantic search** | ✅ (with neural plugin) | ✅ (native semantic ranking) | ✅ |
| **Vector search** | ✅ (k-NN plugin) | ✅ (native) | ✅ (native) |
| **AWS → Azure** | OpenSearch ≈ Azure AI Search | | |
| **AWS → GCP** | OpenSearch ≈ Vertex AI Vector Search | | |
| **AI use case** | RAG pipelines, document Q&A, semantic search over large corpora |
| **Free alternatives** | **FAISS** (local, no cost), **Chroma** (local, no cost), **Qdrant** (cloud free tier), **Weaviate** (cloud free tier) |
| **Notes** | **Azure AI Search free tier is by far the best for learning.** OpenSearch has no free tier. Vertex AI Vector Search has no free tier. |

---

## 12. Secrets Management

*Store API keys, connection strings, credentials. Never put these in code.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | Secrets Manager | Key Vault | Secret Manager |
| **Free tier** | ❌ $0.40/secret/month | ✅ 10,000 transactions/month 🏆 | ✅ 6 active versions + 10K ops free 🏆 |
| **Managed Identity** | IAM Roles (for EC2/ECS/Lambda) | Managed Identity | Workload Identity |
| **AWS → Azure** | Secrets Manager = Key Vault | IAM Role = Managed Identity | |
| **AWS → GCP** | Secrets Manager = Secret Manager | IAM Role = Workload Identity | |
| **AI use case** | Store OpenAI API keys, database passwords, Langfuse keys — without putting them in `.env` files |
| **Notes** | **Managed Identity / IAM Roles / Workload Identity** is the pattern where your app gets credentials automatically from the cloud — no API keys in code at all. This is the production-correct approach. AWS Secrets Manager is the only one that costs money from the first secret. |

---

## 13. API Gateway

*Manage, secure, and route HTTP APIs.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | API Gateway | API Management | Cloud Endpoints / Apigee |
| **Free tier** | ✅ 1M API calls/month (12 months) | ❌ (~$35/month for Developer tier) | ✅ Cloud Endpoints: 2M calls/month 🏆 |
| **AWS → Azure** | API Gateway ≈ API Management | | |
| **AWS → GCP** | API Gateway ≈ Cloud Endpoints | | |
| **AI use case** | Rate-limiting AI endpoints, authentication, versioning |
| **Notes** | For simple AI apps, **skip API Management entirely** and use built-in HTTP triggers in Functions or Container Apps. API Management only makes sense when you need auth, rate limiting, and multiple API versions at scale. |

---

## 14. Monitoring & Observability

*Logs, metrics, traces, alerts.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | CloudWatch | Azure Monitor + Application Insights | Cloud Monitoring + Cloud Logging |
| **Free tier** | ✅ 10 metrics, 5GB logs, 1M API calls/month | ✅ 5GB data ingestion/month 🏆 | ✅ 50GB logs/month, 150MB metrics 🏆 |
| **Traces (APM)** | CloudWatch X-Ray | Application Insights | Cloud Trace |
| **Dashboards** | CloudWatch Dashboards | Azure Dashboard / Workbooks | Cloud Monitoring Dashboards |
| **AWS → Azure** | CloudWatch = Azure Monitor | X-Ray = Application Insights | |
| **AWS → GCP** | CloudWatch = Cloud Monitoring + Logging | | |
| **AI use case** | Track LLM latency, cost per request, error rates, token usage |
| **LLM-specific** | 🏆 **Langfuse** (langfuse.com) — purpose-built for LLM apps. Free cloud tier. Use this alongside any of the above. |

---

## 15. Container Registry

*Store Docker images.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | ECR | ACR (Azure Container Registry) | Artifact Registry |
| **Free tier** | ❌ $0.10/GB/month | ❌ Basic tier ~$5/month | ⚠️ 0.5GB free |
| **AWS → Azure** | ECR = ACR | | |
| **AWS → GCP** | ECR = Artifact Registry | | |
| **Free alternatives** | 🏆 **GitHub Container Registry** (ghcr.io) — free for public repos, included in all GitHub plans | | |
| **Notes** | For learning, use **GitHub Container Registry** instead of paying for ACR, ECR, or Artifact Registry. Container Apps and Cloud Run can pull from ghcr.io directly. |

---

## 16. CI/CD

*Automate build → test → deploy pipelines.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | CodePipeline + CodeBuild | Azure DevOps / GitHub Actions | Cloud Build |
| **Free tier** | ❌ $1/active pipeline/month | ✅ GitHub Actions: 2,000 min/month 🏆 | ✅ 120 build-min/day |
| **AWS → Azure** | CodePipeline = Azure Pipelines (or GitHub Actions) | | |
| **AWS → GCP** | CodePipeline = Cloud Build | | |
| **AI use case** | Auto-deploy AI apps when you push code |
| **Notes** | **GitHub Actions is the clear winner.** Free, powerful, you already know it, and it deploys to all three clouds equally well. Use GitHub Actions for everything — don't touch CodePipeline, Azure DevOps, or Cloud Build unless forced to. |

---

## 17. Identity & Access

*Who can access what. Service-to-service auth.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | IAM | Entra ID (was: Azure AD) + RBAC | IAM |
| **User auth** | Cognito | Entra External ID (B2C) | Firebase Auth / Identity Platform |
| **Service auth** | IAM Roles for EC2/Lambda | Managed Identity | Workload Identity |
| **Free tier** | ✅ IAM is always free | ✅ Entra ID free tier (50K objects) | ✅ IAM is always free |
| **AWS → Azure** | IAM Role = Managed Identity | Cognito = Entra External ID | |
| **AWS → GCP** | IAM Role = Workload Identity | Cognito = Firebase Auth | |
| **AI use case** | Let your AI app read from Blob Storage / Secret Manager without API keys in code |
| **Notes** | The pattern "give your app an identity so it can access cloud resources without credentials" is called **Managed Identity (Azure)**, **IAM Role** (AWS), or **Workload Identity (GCP)**. Same concept, different name. Learn this early — it's the production-correct way to handle secrets. |

---

## 18. Messaging & Events

*Decouple services. Async processing.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Queue** | SQS | Queue Storage / Service Bus | Cloud Pub/Sub |
| **Events** | EventBridge | Event Grid | Cloud Eventarc |
| **Pub/Sub** | SNS | Service Bus Topics | Cloud Pub/Sub |
| **Free tier** | ✅ SQS: 1M requests/month | ✅ Queue Storage: free with storage account | ✅ Pub/Sub: 10GB/month 🏆 |
| **AWS → Azure** | SQS = Queue Storage (simple) or Service Bus (features) | SNS = Event Grid | |
| **AWS → GCP** | SQS = Cloud Pub/Sub | SNS = Cloud Pub/Sub | |
| **AI use case** | Queue long-running AI jobs, async document processing, decouple ingestion from inference |

---

## 19. Static Web Hosting

*Host HTML/CSS/JS websites. No backend.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | S3 + CloudFront, or Amplify | Static Web Apps | Firebase Hosting |
| **Free tier** | ✅ S3 + CloudFront (12 months) | ✅ 100GB bandwidth/month (always free) 🏆 | ✅ 10GB storage + 360MB/day transfer |
| **GitHub integration** | ✅ Amplify | ✅ Built-in (auto-deploys from GitHub) 🏆 | ✅ Firebase CLI |
| **AWS → Azure** | Amplify ≈ Static Web Apps | | |
| **AWS → GCP** | Amplify ≈ Firebase Hosting | | |
| **AI use case** | Front-end for AI apps, demo pages, documentation |
| **Notes** | Azure Static Web Apps has the smoothest GitHub Actions integration — push to main, it auto-deploys. |

---

## 20. Infrastructure as Code

*Define infrastructure in code. Reproducible, version-controlled deployments.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Native IaC** | CloudFormation | ARM Templates / Bicep | Cloud Deployment Manager |
| **Cross-cloud** | 🏆 **Terraform** — works on all three, same syntax, free | | |
| **AWS → Azure** | CloudFormation = ARM Templates (but use Terraform instead) | | |
| **AI use case** | Reproduce your AI infrastructure: OpenAI resource, storage, Container Apps, all in one `terraform apply` |
| **Notes** | **Use Terraform.** You already know it. The `azurerm` provider covers everything you need. Don't learn ARM templates or Bicep unless you're forced to. `azurerm` = `aws` provider, same concept. |

---

## 21. AI Document Processing

*Extract text, tables, and structure from PDFs and images.*

| | AWS | Azure | GCP |
|---|---|---|---|
| **Service** | Textract | Document Intelligence (was: Form Recognizer) | Document AI |
| **Free tier** | ✅ 1,000 pages/month (12 months) | ✅ 500 pages/month (always free) 🏆 | ✅ 1,000 pages/month (12 months) |
| **AI use case** | Extract data from race guides, training plans, lab results for RAG pipelines |

---

## 22. AI Speech (Text-to-Speech + Speech-to-Text)

| | AWS | Azure | GCP |
|---|---|---|---|
| **TTS Service** | Polly | Speech Service | Text-to-Speech API |
| **STT Service** | Transcribe | Speech Service | Speech-to-Text API |
| **TTS Free** | ✅ 5M chars/month (12 months) | ✅ 5h audio/month | ✅ 1M chars/month 🏆 |
| **STT Free** | ✅ 60 min/month (12 months) | ✅ 5h audio/month 🏆 | ✅ 60 min/month |
| **AI use case** | Voice interfaces for AI assistants, transcribing workout notes |

---

## 23. Vector Databases (Third-Party, Cloud-Agnostic)

These work on all three clouds and are often simpler than native solutions for AI/RAG use cases:

| Service | Free Tier | Best For |
|---|---|---|
| **Qdrant** | ✅ 1GB free on Qdrant Cloud | Production RAG, rich filtering |
| **Weaviate** | ✅ 14-day free trial, then paid | Hybrid search (keyword + vector) |
| **Pinecone** | ✅ 1 index free (Serverless tier) | Simple vector search, well-documented |
| **Chroma** | ✅ Open source, run locally | Local development, no cloud needed |
| **FAISS** | ✅ Open source, run locally | Fast local prototyping, no persistence |
| **pgvector** | ✅ Extension for PostgreSQL (free) | If you already have PostgreSQL — just add vectors |

> **For learning RAG:** Start with FAISS or Chroma locally → move to pgvector if you already have a database → use Azure AI Search (free tier) or Qdrant for cloud.

---

## Quick Reference: Free Tier Winners

| Category | Best Free Option |
|---|---|
| Serverless functions | GCP Cloud Functions (2M invocations/month) |
| Containers (no cluster) | GCP Cloud Run or Azure Container Apps (both excellent) |
| PaaS web app | App Engine or Azure App Service |
| Object storage | GCP Cloud Storage (5GB, always free) |
| Relational database | AWS RDS or Azure PostgreSQL (12 months) |
| NoSQL | AWS DynamoDB (always free 25GB) |
| Cache | Upstash (not a cloud native — third-party, all clouds) |
| LLM API | GCP Gemini Flash via AI Studio |
| Vector / Search | Azure AI Search (free tier) |
| Secrets | Azure Key Vault or GCP Secret Manager |
| Container registry | GitHub Container Registry (ghcr.io) |
| CI/CD | GitHub Actions (2,000 min/month) |
| Monitoring | GCP Cloud Logging (50GB/month) |
| Static hosting | Azure Static Web Apps |

---

## The Azure Summer Stack (All Free or Covered by $200 Credit)

| Day | Service | Cost |
|---|---|---|
| 1 | Static Web Apps | ✅ Free forever |
| 2 | Azure OpenAI | ~$0.01 total with GPT-4o-mini |
| 3 | App Service F1 | ✅ Free forever |
| 4 | Blob Storage | ✅ Free 12 months |
| 5 | Key Vault | ✅ Free 10K ops/month |
| 6 | Blob + OpenAI | ✅ + pennies |
| 7–9 | LangChain + OpenAI | ✅ + pennies |
| 10–11 | Azure AI Search | ✅ Free tier (3 indexes, 50MB) |
| 12–14 | LangGraph + OpenAI | ✅ + pennies |
| 15 | Langfuse | ✅ Free cloud tier |
| 16 | Application Insights | ✅ Free 5GB/month |
| 17 | Azure Functions | ✅ Free 1M executions/month |
| 18 | Container Apps | ✅ Free · ACR: ⚠️ $5 (use ghcr.io instead) |
| 19–20 | Capstone (your choice) | ✅ All of the above |
| **Total** | | **~€0.50 in tokens + $0 if using ghcr.io** |
