# Day 11 — "The Expert Assistant"

**Concept:** LangChain + Azure AI Search · Production RAG pipeline · Source citations
**You build:** Rebuild Day 9's RAG bot, but swap the local FAISS vectorstore for Azure AI Search using LangChain's `AzureSearch` vectorstore. Every answer now also prints which document chunk(s) it came from — a source citation, not just a bare answer.

---

## The Goal

Day 9 proved RAG works: PDF → chunks → embeddings → FAISS → retrieve → answer. Day 10 proved Azure AI Search can hold those same vectors persistently and query them with hybrid + semantic search — but you talked to the index directly with the `azure-search-documents` SDK, not through LangChain.

Day 11 closes the loop: LangChain's `AzureSearch` vectorstore wraps Azure AI Search the same way `FAISS` wrapped your in-memory store on Day 9. Same `retriever.as_retriever()` shape, same `RetrievalQA`-style chain — the only thing that changes is where the vectors physically live.

```
Day 9  (FAISS):       PDF → chunks → embeddings → FAISS.from_documents()      → in-memory retriever
Day 10 (raw SDK):      PDF → chunks → embeddings → SearchClient.upload_documents() → manual hybrid query
Day 11 (LangChain):    PDF → chunks → embeddings → AzureSearch.from_documents()  → retriever.as_retriever() → same chain shape as Day 9
```

The second new idea today is **citations**: instead of just printing an answer, you keep `return_source_documents=True` (same flag from Day 9) and print the page number + snippet for every chunk that fed the answer. That's the difference between "trust me" and "here's proof."

---

## Step 0 — Confirm your Day 10 resources are still live

- [X] Confirm the `summer-search` service still exists and is reachable:

```bash
az search service show \
  --name summer-search --resource-group summer-rg \
  --query "provisioningState" -o tsv
```
→ should print `Succeeded`

- [X] Confirm your project-root `.env` still has all four values from Days 9–10:

```
AZURE_OPENAI_KEY=...
AZURE_SEARCH_ENDPOINT=https://summer-search.search.windows.net
AZURE_SEARCH_KEY=...
```

- [X] Copy the same PDF you used on Day 9/10 into `day11/`:

```bash
cp day9/document.pdf day11/document.pdf
```

---

## Step 1 — Install dependencies

- [X] Create `day11/requirements.txt`:

```
python-dotenv
langchain-openai
langchain-community
langchain-classic
langchain-text-splitters
azure-search-documents>=11.4.0
pypdf
```

- [X] Install:

```bash
cd day11
pip3.11 install -r requirements.txt
```

---

## Step 2 — Ingest through LangChain's `AzureSearch` vectorstore

This replaces Day 10's manual `create_index.py` + `ingest.py`. `AzureSearch.from_documents()` creates its own index (with its own field layout: `id`, `content`, `content_vector`, `metadata`) and uploads the embedded chunks in one call — you don't hand-write the schema this time, LangChain does it for you.

- [X] Create `day11/ingest.py`:

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv("../.env")

AZURE_OPENAI_ENDPOINT = "https://summer-openai-c20b7.openai.azure.com/"
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "summer-docs-langchain"   # separate from Day 10's hand-built "summer-docs" index

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)

# --- Load + chunk, same as Day 9 ---
loader = PyPDFLoader("document.pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
print(f"Loaded {len(docs)} pages, split into {len(chunks)} chunks.")

# --- LangChain creates the index AND uploads the embedded chunks ---
vectorstore = AzureSearch(
    azure_search_endpoint=SEARCH_ENDPOINT,
    azure_search_key=SEARCH_KEY,
    index_name=INDEX_NAME,
    embedding_function=embeddings.embed_query,
)
vectorstore.add_documents(documents=chunks)
print(f"Uploaded {len(chunks)} chunks to index '{INDEX_NAME}'.")
```

- [X] Run it:

```bash
python ingest.py
```
→ should print the chunk count and `Uploaded N chunks to index 'summer-docs-langchain'.`

- [X] In the [Azure Portal](https://portal.azure.com) → `summer-search` → **Indexes**, confirm `summer-docs-langchain` now exists alongside Day 10's `summer-docs`. Open it and compare its fields to Day 10's manually-defined schema — notice LangChain added its own `metadata` field.

> **Ignorable warning:** after `Uploaded N chunks...` prints, you may see `Exception ignored in: <function AzureSearch.__del__ ...> ModuleNotFoundError: import of asyncio halted`. This fires during Python's interpreter shutdown, when `AzureSearch`'s `__del__` tries to close an internal async HTTP session after `asyncio` is already partially torn down. It's a known quirk in `langchain_community`'s `AzureSearch` wrapper — it happens *after* the upload already succeeded and doesn't affect the ingested data. Verify success via the portal or a count query, not by the absence of this traceback.

---

## Step 3 — Build the RAG chain with citations

Same shape as Day 9's `main.py`: a retriever backed by a vectorstore, wired into `RetrievalQA` with `return_source_documents=True`. The only line that changed from Day 9 is which vectorstore the retriever comes from.

- [X] Create `day11/main.py`:

```python
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_classic.chains import RetrievalQA

load_dotenv("../.env")

AZURE_OPENAI_ENDPOINT = "https://summer-openai-c20b7.openai.azure.com/"
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "summer-docs-langchain"
API_KEY = os.getenv("AZURE_OPENAI_KEY")

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=API_KEY,
)

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=API_KEY,
)

# --- The only real difference from Day 9: FAISS → AzureSearch ---
vectorstore = AzureSearch(
    azure_search_endpoint=SEARCH_ENDPOINT,
    azure_search_key=SEARCH_KEY,
    index_name=INDEX_NAME,
    embedding_function=embeddings.embed_query,
)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_type="similarity", k=4),
    return_source_documents=True,
)

if __name__ == "__main__":
    while True:
        question = input("Ask a question about the document ('quit' to exit): ")
        if question.lower() == "quit":
            break

        result = qa.invoke(question)
        print("\n--- Answer ---")
        print(result["result"])
        print("\n--- Sources ---")
        for i, doc in enumerate(result["source_documents"], start=1):
            page = doc.metadata.get("page", "?")
            print(f"[{i}] (page {page}) {doc.page_content[:150]}...")
        print()
```

- [X] Run it:

```bash
python main.py
```

---

## Step 4 — Verify citations and compare against Day 9/10

- [X] Ask one of the same questions you used on Day 9. The answer should match, and the printed source(s) should contain the fact used in the answer — same verification logic as Day 9, now backed by Azure AI Search instead of memory.
- [X] Ask a question with multiple plausible source chunks (e.g. something mentioned on two different pages). Confirm `--- Sources ---` lists more than one citation and each `[n]` marker corresponds to a distinct page/snippet.
- [X] In the Azure Portal, open `summer-docs-langchain` → **Search explorer**, run `*`, and confirm the document count matches `len(chunks)` from Step 2 — proof the answers really are backed by the persisted index, not a leftover in-memory object.
- [X] `grep -r "sk-" day11/` returns nothing — keys still come from `.env`.

Expected output shape:

```
Ask a question about the document ('quit' to exit): what time does transition 1 close?

--- Answer ---
Transition 1 closes at 7:15 AM.

--- Sources ---
[1] (page 3) T1 opens at 5:30 AM and closes strictly at 7:15 AM. Athletes arriving...
[2] (page 4) Late arrivals after T1 closure will be marked as a DNS for the swim...
```

---

## Mental Model

```
document.pdf
      │
      ▼
PyPDFLoader + RecursiveCharacterTextSplitter        → same chunks as Day 9/10
      │
      ▼
AzureSearch.from_documents(chunks, embeddings)      → LangChain creates the index AND uploads vectors
      │                                                  (Day 9: FAISS in memory · Day 10: raw SearchClient calls)
      ▼
vectorstore.as_retriever(search_type="similarity")  → same retriever interface as Day 9's FAISS retriever
      │
      ▼
RetrievalQA.from_chain_type(llm, retriever, return_source_documents=True)
      │
      ▼
qa.invoke(question) ──► answer + source_documents[] ──► print citations per chunk
```

The chain shape never changes across Days 9–11 — `retriever → llm → answer + sources`. What moved is the storage layer underneath the retriever: process memory (Day 9) → a manually-schemed Azure AI Search index queried directly (Day 10) → the same Azure AI Search service, now managed through LangChain's own index and retriever abstraction (Day 11). Day 12 leaves RAG behind and starts LangGraph — state machines instead of linear chains.

---
