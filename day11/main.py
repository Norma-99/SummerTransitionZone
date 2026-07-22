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