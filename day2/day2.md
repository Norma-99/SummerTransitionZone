# Day 2 — "Ask the Machine"

**Concept:** Azure OpenAI Service · API keys · First model call from Python
**You build:** A Python script that asks GPT-4o-mini a question and prints the answer.

---

## Commands Used and explanation

- [X] Log In into Azure `az login` 
- [X] Run the command to create a group: `az group create --name summer-rg --location westeurope`
- [X] Enable Microsoft.CognitiveServices: `az provider register --namespace Microsoft.CognitiveServices`
- [X] To check if it was registered: `az provider show --namespace Microsoft.CognitiveServices --query "registrationState" -o tsv`
- [X] Create the account (like signing up for a service)

```bash
az cognitiveservices account create \
  --name summer-openai \
  --resource-group summer-rg \
  --kind OpenAI \
  --sku S0 \
  --location swedencentral
```

| Part | What it means |
|---|---|
| `az cognitiveservices account create` | "Hey Azure, create me an AI services account" |
| `--name summer-openai` | Name it `summer-openai` (your choice, any name works) |
| `--resource-group summer-rg` | Put it inside the folder `summer-rg` you made on Day 1 |
| `--kind OpenAI` | Specifically the OpenAI type (not translation, vision, etc.) |
| `--sku S0` | Use the standard pricing tier (S0 = Standard tier 0) |
| `--location swedencentral` | Host it in Azure's Sweden datacenter |

- [] Get the azure active models list here https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure?tabs=global-standard&pivots=azure-openai 

- [X] To know which models are available to consume put this command: 
```bash
az cognitiveservices usage list --location swedencentral \
--query "[].{Name:name.value, Current:currentValue, Limit:limit}" \
```
- [X] Deploy the model. Installing a specific app inside the account we just created

```bash
az cognitiveservices account deployment create \
  --name summer-openai \
  --resource-group summer-rg \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-name GlobalStandard \
  --sku-capacity 1
```

| Part | What it means |
|---|---|
| `--name summer-openai` | Inside *this* account (the one you just made) |
| `--deployment-name gpt-4o-mini` | Give this deployment a nickname — you'll use this in Python |
| `--model-name gpt-4.1-mini` | Which AI model to use (GPT-4o-mini = fast & cheap) |
| `--model-version "2025-04-14"` | Which exact version of that model |
| `--model-format OpenAI` | It follows the OpenAI API format |
| `--sku-name GlobalStandard` | Use standard capacity (not provisioned/reserved) |
| `--sku-capacity 1` | reserving 1 unit of throughput (K tokens / min) |

- Response obtained: 
```json
{
  "etag": "\"cde0a768-310b-4b2a-8282-b450f81a40eb\"",
  "id": "/subscriptions/8bd4b61b-d4a6-4ab9-9931-e6add213c5fb/resourceGroups/summer-rg/providers/Microsoft.CognitiveServices/accounts/summer-openai/deployments/gpt-4o-mini",
  "name": "gpt-4o-mini",
  "properties": {
    "callRateLimit": null,
    "capabilities": {
      "agentsV2": "true",
      "area": "EUR",
      "assistants": "true",
      "chatCompletion": "true",
      "responses": "true"
    },
    "capacitySettings": null,
    "currentCapacity": 1,
    "deploymentState": "Running",
    "dynamicThrottlingEnabled": null,
    "model": {
      "callRateLimit": null,
      "format": "OpenAI",
      "name": "gpt-4.1-mini",
      "publisher": null,
      "source": null,
      "sourceAccount": null,
      "version": "2025-04-14"
    },
    "parentDeploymentName": null,
    "provisioningState": "Succeeded",
    "raiPolicyName": "Microsoft.DefaultV2",
    "rateLimits": [
      {
        "count": 1.0,
        "dynamicThrottlingEnabled": null,
        "key": "request",
        "matchPatterns": null,
        "minCount": null,
        "renewalPeriod": 60.0
      },
      {
        "count": 1000.0,
        "dynamicThrottlingEnabled": null,
        "key": "token",
        "matchPatterns": null,
        "minCount": null,
        "renewalPeriod": 60.0
      }
    ],
    "routing": null,
    "scaleSettings": null,
    "serviceTier": null,
    "spilloverDeploymentName": null,
    "versionUpgradeOption": "OnceNewDefaultVersionAvailable"
  },
  "resourceGroup": "summer-rg",
  "sku": {
    "capacity": 1,
    "family": null,
    "name": "GlobalStandard",
    "size": null,
    "tier": null
  },
  "systemData": {
    "createdAt": "2026-06-25T17:14:48.268799+00:00",
    "createdBy": "normagutiesc@gmail.com",
    "createdByType": "User",
    "lastModifiedAt": "2026-06-25T17:14:48.268799+00:00",
    "lastModifiedBy": "normagutiesc@gmail.com",
    "lastModifiedByType": "User"
  },
  "tags": null,
  "type": "Microsoft.CognitiveServices/accounts/deployments"
}
```

- [X] To get the endpoint run: (endpoint: https://summer-openai-c20b7.openai.azure.com/)

```bash
az cognitiveservices account show \
  --name summer-openai \
  --resource-group summer-rg \
  --query "properties.endpoint" \
  --output tsv
```

- [X] To get the API KEY run: 

```bash
# Get your API key
az cognitiveservices account keys list \
  --name summer-openai \
  --resource-group summer-rg \
  --query "key1" \
  --output tsv
```
---

### Python Code — Talking to the AI

```python
from openai import AzureOpenAI          # Import the Azure OpenAI library
```
Brings in the tool that knows how to talk to Azure's AI.

```python
client = AzureOpenAI(
    api_key="...",                       # Your secret password to Azure
    api_version="2024-02-01",           # Which version of the API to use
    azure_endpoint="https://summer-openai.openai.azure.com/"  # Your account's URL
)
```
Creates a **connection** to your Azure account. Like logging in.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",               # Use the deployment you named above
    messages=[{"role": "user", "content": "Explain Azure in one sentence."}]
)
```
Sends a **message** to the AI — like typing in a chat box. The `role: user` means it's your message (vs. `assistant` which is the AI's reply).

```python
print(response.choices[0].message.content)
```
Prints what the AI said back. `choices[0]` = the first (and usually only) response.

---

### Mental Model

```
You (Python) → Azure Account (summer-openai) → Deployed Model (gpt-4o-mini) → AI responds → You print it
```

The two bash commands set up the infrastructure once. The Python script is what you run every time you want to ask a question.
