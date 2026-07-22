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