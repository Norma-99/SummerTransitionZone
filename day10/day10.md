# Day 10 — "The Real Search Engine"

**Concept:** Azure AI Search · Index schema · Vector search · Semantic search
**You build:** Replace Day 9's local FAISS vectorstore with Azure AI Search — the production-grade, managed version. Same PDF, same embeddings model, but the vectors now live in a real search service with a defined index schema instead of in a Python process's memory.

---

## The Goal

Day 9's RAG bot worked, but FAISS has a hard limitation: it's an in-memory index that lives only as long as your script runs. Nothing is persisted, nothing is shared between processes, and there's no way to filter, scale, or manage it as your document set grows. That's fine for learning RAG — it's not fine for production.

Azure AI Search is the managed equivalent of FAISS/Pinecone: a real service with a defined **index schema** (like a database table), native **vector search** (nearest-neighbour search over embeddings, same idea as FAISS but persisted and scalable), and **semantic search** (Microsoft's L2 re-ranker that reorders results by actual relevance to the query, not just vector distance).

```
Day 9  (FAISS):     PDF → chunks → embeddings → in-memory vectors → gone when script exits
Day 10 (AI Search):  PDF → chunks → embeddings → uploaded to a persistent index → query anytime
```

Today you build and query the index directly. Day 11 wires it back into a LangChain RAG chain with source citations — the same shape as Day 9, just backed by Azure AI Search instead of FAISS.

---

## Step 0 — Create the Azure AI Search service

- [X] Create the service (free tier: 50 MB storage, 3 indexes — plenty for this exercise):

```bash
az search service create \
  --name summer-search \
  --resource-group summer-rg \
  --sku free \
  --location westeurope
```

- [X] Confirm it's provisioned:

```bash
az search service show \
  --name summer-search --resource-group summer-rg \
  --query "provisioningState" -o tsv
```
→ should print `Succeeded`

- [X] Get the admin key (needed to create indexes and upload documents):

```bash
az search admin-key show \
  --service-name summer-search --resource-group summer-rg \
  --query primaryKey -o tsv
```

- [X] Add to your `.env` (project root):

```
AZURE_SEARCH_ENDPOINT=https://summer-search.search.windows.net
AZURE_SEARCH_KEY=<the primary key from above>
```

---

## Step 1 — Reuse Day 9's assets

- [X] Copy the same PDF into `day10/`:

```bash
cp day9/document.pdf day10/document.pdf
```

- [X] Confirm your `.env` still has `AZURE_OPENAI_KEY` and the `text-embedding-3-small` deployment from Day 9 is live:

```bash
az cognitiveservices account deployment show \
  --name summer-openai --resource-group summer-rg \
  --deployment-name text-embedding-3-small \
  --query "properties.provisioningState" -o tsv
```
→ should print `Succeeded`

---

## Step 2 — Install dependencies

- [X] Add to `day10/requirements.txt`:

```
python-dotenv
azure-search-documents>=11.4.0
langchain-openai
langchain-community
langchain-text-splitters
pypdf
```

- [X] Install:

```bash
cd day10
pip3.11 install -r requirements.txt
```

---

## Step 3 — Define the index schema

This is the concept the "done when" check cares most about: an index isn't just "a bunch of vectors," it's a schema, like a table. Each field has a type and a role (searchable text, filterable metadata, or a vector field).

- [X] Create `day10/create_index.py`:

```python
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField, SemanticSearch,
)

load_dotenv("../.env")

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "summer-docs"

# text-embedding-3-small produces 1536-dimensional vectors
EMBEDDING_DIMENSIONS = 1536

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=EMBEDDING_DIMENSIONS,
        vector_search_profile_name="vector-profile",
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
    profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-config")],
)

semantic_search = SemanticSearch(
    configurations=[
        SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            ),
        )
    ],
    default_configuration_name="semantic-config",
)

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
)

index_client = SearchIndexClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
index_client.create_or_update_index(index)
print(f"Index '{INDEX_NAME}' created.")
```

- [X] Run it:

```bash
python create_index.py
```
→ should print `Index 'summer-docs' created.`

- [ ] Open the [Azure Portal](https://portal.azure.com) → your `summer-search` resource → **Indexes** → confirm `summer-docs` exists and inspect its fields. This is the "index schema" the Done-when check asks about: a fixed set of typed fields, one of which (`content_vector`) is a vector field instead of plain text.

---

## Step 4 — Chunk, embed, and upload the document

Same chunking logic as Day 9 — the difference is where the vectors end up.

- [X] Create `day10/ingest.py`:

```python
import os, uuid
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv("../.env")

AZURE_OPENAI_ENDPOINT = "https://summer-openai-c20b7.openai.azure.com/"
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "summer-docs"

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

# --- Embed every chunk in one batch call ---
vectors = embeddings.embed_documents([c.page_content for c in chunks])

# --- Shape each chunk into a document matching the index schema ---
search_docs = [
    {
        "id": str(uuid.uuid4()),
        "page": chunk.metadata.get("page", 0),
        "content": chunk.page_content,
        "content_vector": vector,
    }
    for chunk, vector in zip(chunks, vectors)
]

search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
result = search_client.upload_documents(documents=search_docs)
print(f"Uploaded {sum(r.succeeded for r in result)}/{len(result)} chunks.")
```

- [X] Run it:

```bash
python ingest.py
```
→ should print the chunk count and `Uploaded N/N chunks.`

- [X] In the portal, go to `summer-docs` → **Search explorer** → run an empty query (`*`) → confirm the document count matches.

---

## Step 5 — Run a vector + semantic query

- [X] Create `day10/query.py`:

```python
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv("../.env")

AZURE_OPENAI_ENDPOINT = "https://summer-openai-c20b7.openai.azure.com/"
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "summer-docs"

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=os.getenv("AZURE_OPENAI_KEY"),
)
search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))

if __name__ == "__main__":
    while True:
        question = input("Ask a question about the document ('quit' to exit): ")
        if question.lower() == "quit":
            break

        vector_query = VectorizedQuery(
            vector=embeddings.embed_query(question),
            k_nearest_neighbors=4,
            fields="content_vector",
        )

        results = search_client.search(
            search_text=question,          # keyword half of the hybrid query
            vector_queries=[vector_query],  # vector half of the hybrid query
            query_type="semantic",
            semantic_configuration_name="semantic-config",
            select=["content", "page"],
            top=4,
        )

        print("\n--- Top matches (hybrid + semantic re-ranked) ---")
        for r in results:
            print(f"(page {r['page']}, rerank score {r.get('@search.reranker_score')}) {r['content'][:150]}...")
        print()
```

- [ ] Run it:

```bash
python query.py
```

- [X] Ask one of the same questions you used in Day 9. Compare the top chunk returned here against the FAISS result — it should surface the same (or an equally relevant) piece of text.

---

> Free tier note: semantic ranking on the `free` SKU is capped at a small monthly query quota. If `query_type="semantic"` errors out on your subscription, drop it to `query_type="simple"` — you'll still get hybrid vector + keyword search, just without the re-ranker.

---

## Mental Model

```
document.pdf
      │
      ▼
PyPDFLoader + RecursiveCharacterTextSplitter     → same chunks as Day 9
      │
      ▼
embeddings.embed_documents(chunks)               → same vectors as Day 9
      │
      ▼
SearchClient.upload_documents(...)               → vectors persisted in Azure AI Search
                                                        (Day 9: kept in-memory FAISS instead)
      │
question ──► embeddings.embed_query() ──► VectorizedQuery
                                                │
                                                ▼
                          search_client.search(text + vector, query_type="semantic")
                                                │
                                    ┌───────────┴───────────┐
                                    ▼                       ▼
                          keyword match (BM25)     vector similarity (HNSW)
                                    │                       │
                                    └───────────┬───────────┘
                                                ▼
                                  semantic re-ranker reorders by relevance
                                                │
                                                ▼
                                  top chunks returned (survives process restarts)
```

The retrieval shape is identical to Day 9 — embed the question, find the closest chunks, hand them to an LLM. What changed is *where the index lives*: a managed, persistent service instead of a variable in your script. Day 11 puts the LLM back on top of this index via LangChain's `AzureSearch` vectorstore, so the full RAG chain (with source citations) reads the same way it did on Day 9.

---
