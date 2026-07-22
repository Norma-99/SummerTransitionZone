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