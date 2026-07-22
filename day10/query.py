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