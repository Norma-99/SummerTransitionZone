# Day 5 — "No Keys Under the Mat"

**Concept:** Azure Key Vault · Managed Identity · Secret management without `.env` files
**You build:** Your Day 3 chatbot, but now it reads secrets from Key Vault instead of environment variables — and uses Managed Identity (no credentials at all in code).

---

## The Goal

Right now `AZURE_OPENAI_KEY` lives as a plaintext App Service setting (set that way back in [day3/day3.md](../day3/day3.md)). Day 5 removes it entirely: the key moves into Key Vault, and the app authenticates to Key Vault using the App Service's own **Managed Identity** — no key, connection string, or credential anywhere in your code or config.

---

## Step 0 -- Login
- [X] Run: `az login --tenant "a8598645-9ccc-445a-afb3-0fa42c52d056" --scope "https://management.core.windows.net//.default"` 
- [X] Enable Microsoft.CognitiveServices: `az provider register --namespace Microsoft.KeyVault`
- [X] To check if it was registered: `az provider show --namespace Microsoft.KeyVault --query "registrationState" -o tsv`
 [X] Set Vault permissions (needed because new vaults default to RBAC authorization — creating the vault does not automatically grant you a data-plane role, so `keyvault secret set` 403s without this):

```bash
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee-object-id a869f408-2cb8-45fb-9e7f-aba515d2a36e \
  --assignee-principal-type User \
  --scope /subscriptions/8bd4b61b-d4a6-4ab9-9931-e6add213c5fb/resourcegroups/summer-rg/providers/microsoft.keyvault/vaults/summer-kv
```
RBAC changes can take a minute or two to propagate.
---

## Step 1 — Create the Key Vault

- [X] Run:

```bash
az keyvault create \
  --name summer-kv \
  --resource-group summer-rg \
  --location westeurope
```

Vault names are globally unique (like storage accounts) — if `summer-kv` is taken, add a suffix like you did with `summer-openai-c20b7`.

---

## Step 2 — Store your existing OpenAI key as a secret

- [X] Pull it straight from your `.env` (same trick used in Day 3):

```bash
az keyvault secret set \
  --vault-name summer-kv \
  --name openai-key \
  --value "$(grep AZURE_OPENAI_KEY ../.env | cut -d'=' -f2)" \
  --query "name" -o tsv 2>&1 || true
```

---

## Step 3 — Enable Managed Identity on `summer-chatbot`

- [X] Run:

```bash
az webapp identity assign \
  --name summer-chatbot \
  --resource-group summer-rg
```

This returns a JSON blob with a `principalId` — that's your web app's own Azure AD identity (not you, not an API key — the *app itself* is now a security principal).

- [X] Capture it into a variable for the next step:

```bash
IDENTITY_ID=$(az webapp identity show \
  --name summer-chatbot \
  --resource-group summer-rg \
  --query principalId -o tsv)
```

---

## Step 4 — Grant that identity access to the vault

Check which access model your vault uses:

```bash
az keyvault show --name summer-kv --query properties.enableRbacAuthorization
```

- [X] If `false` (legacy access-policy model):

```bash
az keyvault set-policy \
  --name summer-kv \
  --object-id $IDENTITY_ID \
  --secret-permissions get list
```

- [X] If `true` (Azure RBAC model — the direction Microsoft is pushing):

```bash
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee-object-id $IDENTITY_ID \
  --assignee-principal-type ServicePrincipal \
  --scope $(az keyvault show --name summer-kv --resource-group summer-rg --query id -o tsv)
```

---

## Step 5 — Update `requirements.txt`

- [X] Add to `day5/requirements.txt`:

```
streamlit
openai
azure-identity
azure-keyvault-secrets
```

---

## Step 6 — Write `app.py` to fetch the key from Key Vault

- [X] Create `day5/app.py`:

```python
import streamlit as st
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url="https://summer-kv.vault.azure.net/", credential=credential)
openai_key = kv_client.get_secret("openai-key").value

client = AzureOpenAI(
    api_key=openai_key,
    api_version="2024-02-01",
    azure_endpoint="https://summer-openai-c20b7.openai.azure.com/"
)

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

Notice: no `load_dotenv()`, no `os.getenv`. There's no secret to load from an env file anymore. `DefaultAzureCredential` automatically detects it's running inside App Service and uses the Managed Identity — no code path change needed between local and deployed.

---

## Step 7 — (Optional) Test locally first

`DefaultAzureCredential` falls back to your Azure CLI login when not running in Azure, so as long as you're `az login`'d, it works locally too — but *your* account also needs `get`/`list` (or the RBAC role) on the vault. Add yourself the same way you added the app's identity in Step 4, using your own object ID:

```bash
az ad signed-in-user show --query id -o tsv
```

- [X] Run it locally:

```bash
cd day5
streamlit run app.py
```

---

## Step 8 — Remove the old plaintext key from App Service settings

- [X] Delete it — the whole point is no secrets in config either:

```bash
az webapp config appsettings delete \
  --name summer-chatbot \
  --resource-group summer-rg \
  --setting-names AZURE_OPENAI_KEY
```

---

## Step 9 — Package and deploy

- [X] Zip and deploy:

```bash
cd day5
zip deploy.zip app.py requirements.txt
as webapp start
az webapp deploy \
  --name summer-chatbot \
  --resource-group summer-rg \
  --src-path deploy.zip \
  --type zip
```

---

## Step 10 — Verify

- [X] Visit `https://summer-chatbot.azurewebsites.net` and confirm the chatbot still answers.
- [X] `grep -r AZURE_OPENAI_KEY day5/` returns nothing (no key in code).
- [X] `az webapp config appsettings list --name summer-chatbot --resource-group summer-rg --output table` shows no OpenAI key.
- [X] In the portal, Key Vault → `summer-kv` → **Access policies** (or **IAM** if RBAC) shows `summer-chatbot` as the only app-level entry, with only `get`/`list`.

---

## Step 11 -- Don't forget to stop the app

Use this command: `az webapp stop --name summer-chatbot --resource-group summer-rg`

## Mental Model

```
Old way (Day 3)                       New way (Day 5)
────────────────                      ────────────────────────────────────
App Service setting                   App Service → Managed Identity
  AZURE_OPENAI_KEY = "sk-..."           (no secret, just an Azure AD identity)
       ↓                                        ↓
  app.py reads os.getenv(...)          identity authenticates to Key Vault
                                                 ↓
                                        app.py calls client.get_secret("openai-key")
                                                 ↓
                                        key is fetched at runtime, never stored
```

This is the production pattern: credentials never touch source control, `.env` files, or App Service config — they exist only inside Key Vault, unlocked at runtime by an identity Azure itself manages.

