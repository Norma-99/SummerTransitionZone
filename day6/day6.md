# Day 6 — "Read the Document"

**Concept:** Combining Blob Storage + Azure OpenAI · Building your first useful AI tool
**You build:** Upload a PDF to Blob Storage → download it back → extract its text → summarise it with AI → get a clean bullet-point summary.

---

## The Goal

Days 4 and 5 taught you two separate skills: storing files in Blob Storage, and calling Azure OpenAI safely (via Key Vault + Managed Identity locally through your CLI login). Day 6 wires them together into one pipeline — the shape almost every "AI over my documents" tool takes:

```
PDF file  →  Blob Storage  →  download bytes  →  extract text  →  send to GPT-4o-mini  →  summary
```

This is the same pattern behind "chat with your PDF" products, just without the RAG/search layer yet (that comes in Week 3–4).

---

## Step 0 — Confirm your prior resources are ready

No new resource providers to register today — you're reusing what already exists.

- [X] Confirm your storage account is reachable: `az storage account show --name summerstorage2026 --resource-group summer-rg --query provisioningState -o tsv` → should print `Succeeded`
- [X] Confirm your Key Vault secret is still there: `az keyvault secret show --vault-name summer-kv --name openai-key --query name -o tsv` → should print `openai-key`
- [X] `az login` if your session has expired (`DefaultAzureCredential` falls back to your CLI login locally, same as Day 5)

---

## Step 1 — Create a container for documents

CSVs from Day 4 live in `training-logs`. PDFs get their own drawer: `documents`.

- [X] Add this to the top of your script (or run once via CLI) — the code in Step 5 also does this automatically:

```bash
az storage container create \
  --account-name summerstorage2026 \
  --name documents \
  --auth-mode login
```

---

## Step 2 — Get a real PDF to work with

- [X] Drop any real PDF into `day6/` — a training plan, a race guide, a paper, anything with actual paragraphs of text. Name it `sample_document.pdf`.

---

## Step 3 — Install dependencies

- [X] Add to `day6/requirements.txt`:

```
python-dotenv
azure-storage-blob
azure-identity
azure-keyvault-secrets
openai
PyMuPDF
```

- [X] Install:

```bash
cd day6
pip3.11 install -r requirements.txt
```

`PyMuPDF` installs as the `fitz` module — that mismatch between package name and import name trips people up, so note it now.

---

## Step 4 — Write `main.py`

- [X] Create `day6/main.py`:

```python
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI
import fitz  # PyMuPDF

load_dotenv("../.env")

# --- Blob Storage: connect + ensure container exists ---
blob_client = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)
container = blob_client.get_container_client("documents")
try:
    container.create_container()
    print("Container 'documents' created.")
except Exception:
    print("Container 'documents' already exists, skipping.")

# --- Upload the sample PDF ---
PDF_NAME = "sample_document.pdf"
with open(PDF_NAME, "rb") as f:
    container.upload_blob(PDF_NAME, f, overwrite=True)
    print(f"Uploaded: {PDF_NAME}")

# --- Key Vault: fetch the OpenAI key (same pattern as Day 5) ---
credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url="https://summer-kv.vault.azure.net/", credential=credential)
openai_key = kv_client.get_secret("openai-key").value

openai_client = AzureOpenAI(
    api_key=openai_key,
    api_version="2024-02-01",
    azure_endpoint="https://summer-openai-c20b7.openai.azure.com/"
)


def summarise_document(blob_name: str) -> str:
    # 1. Download the PDF bytes back from Blob Storage
    pdf_bytes = container.download_blob(blob_name).readall()

    # 2. Extract raw text from every page
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    print(f"Extracted {len(text)} characters from {len(doc)} page(s).")

    # 3. Summarise with AI
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarise this document in 5 bullet points."},
            {"role": "user", "content": text[:8000]}  # token limit safety
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    summary = summarise_document(PDF_NAME)
    print("\n--- Summary ---")
    print(summary)
```

---

## Step 5 — Run it

- [X] Run from inside `day6/`:

```bash
cd day6
python main.py
```

Expected output shape:

```
Container 'documents' created.
Uploaded: sample_document.pdf
Extracted 4211 characters from 3 page(s).

--- Summary ---
- Point one from the document
- Point two from the document
- ...
```

---

## Step 6 — Verify

`main.py` authenticates via the account **key** (baked into the connection string), but the CLI command below defaults to `--auth-mode login`, which authenticates as *your own Azure AD user* against the storage **data plane** — a separate permission system from the account key, and one you haven't been granted access to yet. This is the same RBAC gap Day 5 hit with Key Vault, just on Blob Storage this time.

- [X] Grant yourself a data-plane role on the storage account (one-time):

```bash
az role assignment create \
  --role "Storage Blob Data Reader" \
  --assignee-object-id $(az ad signed-in-user show --query id -o tsv) \
  --assignee-principal-type User \
  --scope $(az storage account show --name summerstorage2026 --resource-group summer-rg --query id -o tsv)
```

RBAC changes can take a minute or two to propagate — if the next command still 403s, wait and retry.

- [X] `az storage blob list --account-name summerstorage2026 --container-name documents --auth-mode login --output table` shows `sample_document.pdf`

(Quicker alternative if you don't want to touch RBAC: swap `--auth-mode login` for `--auth-mode key`, which falls back to the same account-key auth `main.py` already uses — no role assignment needed.)
- [X] The printed summary actually reflects the content of your PDF (try a document you know well, and check it isn't hallucinating)
- [X] `grep -r "sk-" day6/` returns nothing — no OpenAI key hardcoded anywhere, it's still coming from Key Vault

---

## Mental Model

```
day6/sample_document.pdf
        │  upload_blob()
        ▼
summerstorage2026 / documents / sample_document.pdf   (Blob Storage)
        │  download_blob().readall()
        ▼
raw PDF bytes  →  fitz.open()  →  page.get_text()  →  plain text
        │
        ▼
openai_client.chat.completions.create(messages=[... text[:8000] ...])
        │
        ▼
5 bullet-point summary
```

The interesting part isn't any single step — it's that Day 4's storage code and Day 2/5's OpenAI code drop in unchanged. This is what "composing Azure services" looks like: each piece stays dumb and single-purpose, and you glue them together in one small function.

---

