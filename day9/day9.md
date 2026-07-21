# Day 9 — "Ask the Library"

**Concept:** RAG (Retrieval-Augmented Generation) · Text splitting · Vector embeddings · Local vectorstore
**You build:** A Q&A bot over a local PDF (e.g. a race guide or training plan). Ask it a question, it finds the relevant chunk of the document and answers from it — not from the model's general knowledge.

---

## The Goal

Day 7 built chains (`prompt | llm | parser`) and Day 8 built an agent that decides which tool to call. Both only know what's in the prompt or what a tool returns — neither can answer questions about *your* documents.

RAG closes that gap in four steps:

```
PDF  →  split into chunks  →  embed each chunk into a vector  →  store vectors locally (FAISS)
                                                                        │
                                            question  →  embed it  →  find closest chunks  →  feed to LLM  →  answer
```

Two new ideas today:
- **Chunking** exists because you can't stuff an entire PDF into a prompt — the context window (and your token budget) is limited. Splitting into overlapping chunks keeps each piece small while not cutting sentences off mid-thought.
- **Embeddings** turn text into a vector of numbers such that semantically similar text ends up close together in vector space. "What time does T1 close?" and "Transition 1 closing time" land near each other even though they share almost no words.

No Azure AI Search today — the vectorstore (FAISS) lives entirely on your machine. That's the point: Day 10–11 will swap this local store for the production Azure AI Search version, but the RAG *logic* here stays the same.

---

## Step 0 — Deploy an embeddings model

Days 2–8 only ever used the `gpt-4o-mini` chat deployment. RAG needs a second deployment: an **embeddings model**, which turns text into vectors instead of generating replies.

- [X] Deploy `text-embedding-3-small` on your existing `summer-openai` resource. Note the SKU: in `swedencentral` (and most regions) this model is only offered as `GlobalStandard`, not `Standard` — using `Standard` fails with `InvalidResourceProperties`:

```bash
az cognitiveservices account deployment create \
  --name summer-openai --resource-group summer-rg \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small --model-version "1" \
  --model-format OpenAI --sku-name GlobalStandard --sku-capacity 1
```

`GlobalStandard` (unlike `Standard`) doesn't default the capacity — omitting `--sku-capacity` fails with `InvalidCapacity`.

- [X] Confirm it's live:

```bash
az cognitiveservices account deployment show \
  --name summer-openai --resource-group summer-rg \
  --deployment-name text-embedding-3-small \
  --query "properties.provisioningState" -o tsv
```
→ should print `Succeeded`

- [X] Confirm your `.env` (at the project root) still has `AZURE_OPENAI_KEY` set — same key as Day 2/7, reused here

---

## Step 1 — Get a PDF to query

- [X] Drop any PDF into `day9/` — a race guide, a training plan, a manual, anything with real content. Name it `day9/document.pdf`.
- [X] Pick 2–3 questions you already know the answer to, straight from the PDF ("what region is the hotel recommendation in?", "What was the API used to extract the hotels information?", "How was it deployed?). You'll use these to verify the bot isn't just guessing.

---

## Step 2 — Install dependencies

- [X] Add to `day9/requirements.txt`:

```
python-dotenv
langchain
langchain-openai
langchain-core
langchain-community
langchain-classic
langchain-text-splitters
pypdf
faiss-cpu
```

- [X] Install:

```bash
cd day9
pip3.11 install -r requirements.txt
```

---

## Step 3 — Write `main.py`

Note: in current LangChain versions, `RecursiveCharacterTextSplitter` lives in its own `langchain_text_splitters` package, and legacy chains like `RetrievalQA` were moved out of `langchain.chains` into `langchain_classic.chains`. If you see `ModuleNotFoundError` for either, that's why — the imports below are already correct.

- [X] Create `day9/main.py`:

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_classic.chains import RetrievalQA

load_dotenv("../.env")

AZURE_ENDPOINT = "https://summer-openai-c20b7.openai.azure.com/"
API_KEY = os.getenv("AZURE_OPENAI_KEY")

# --- The model: same chat deployment as Day 2/7 ---
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
)

# --- The embeddings model: new deployment from Step 0 ---
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    api_version="2024-02-01",
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
)

# --- Load + chunk the PDF ---
loader = PyPDFLoader("document.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# --- Embed each chunk and store the vectors locally ---
vectorstore = FAISS.from_documents(chunks, embeddings)

# --- Wire retrieval + the LLM together ---
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
)


if __name__ == "__main__":
    print(f"Loaded {len(docs)} pages, split into {len(chunks)} chunks.\n")

    while True:
        question = input("Ask a question about the document ('quit' to exit): ")
        if question.lower() == "quit":
            break

        result = qa.invoke(question)
        print("\n--- Answer ---")
        print(result["result"])
        print("\n--- Source chunk(s) used ---")
        for doc in result["source_documents"]:
            print(f"(page {doc.metadata.get('page')}) {doc.page_content[:120]}...")
        print()
```

---

## Step 4 — Run it

- [X] Run from inside `day9/`:

```bash
cd day9
python main.py
```

- [X] Ask one of the questions you picked in Step 1. Confirm the answer matches what's actually in the PDF.
- [X] Ask a question the model could **not** plausibly know without the document (a specific number, name, or date from the PDF). If the answer is correct and the source chunk printed underneath actually contains that fact, RAG is working — the model isn't guessing from training data.
- [X] Ask something *not* in the PDF at all (e.g. "what's the capital of France?") — a well-behaved RAG setup should say it doesn't know, rather than hallucinate an answer from the retrieved chunks.

Expected output shape:

```
Loaded 12 pages, split into 34 chunks.

Ask a question about the document ('quit' to exit): what time does transition 1 close?

--- Answer ---
Transition 1 closes at 7:15 AM...

--- Source chunk(s) used ---
(page 3) T1 opens at 5:30 AM and closes strictly at 7:15 AM. Athletes arriving...
```

---

## Step 5 — Verify

- [X] `len(chunks)` is noticeably larger than `len(docs)` — confirms the splitter actually broke pages into smaller pieces
- [X] The printed source chunk for a correct answer actually contains the fact used in the answer — proves retrieval, not memorisation, drove the response
- [X] Changing `chunk_size` to something small (e.g. `100`) and re-running produces more, smaller chunks and can change (sometimes worsen) answer quality — confirms chunk size is a real tunable, not a cosmetic setting
- [X] `grep -r "sk-" day9/` returns nothing — the key still comes from `.env`, not hardcoded

---

## Mental Model

```
document.pdf
      │
      ▼
PyPDFLoader().load()                        → list of Document objects, one per page
      │
      ▼
RecursiveCharacterTextSplitter(...)          → splits into overlapping ~500-char chunks
      │
      ▼
FAISS.from_documents(chunks, embeddings)     → embeds each chunk, stores vectors in memory
      │
      ▼
question ──► embeddings.embed_query() ──► closest chunks in vector space (via retriever)
                                                    │
                                                    ▼
                                    llm answers using ONLY those chunks as context
                                                    │
                                                    ▼
                                            "Transition 1 closes at 7:15 AM..."
```

The retriever never reads the whole PDF at answer time — it only pulls the `k` chunks whose vectors are closest to the question's vector, and hands just those to the LLM. That's why RAG scales to documents far bigger than any context window: you pay the embedding cost once per chunk, then only ever send a handful of chunks per question. Day 10–11 swap FAISS for Azure AI Search, but this retrieve-then-answer shape stays identical.

---
