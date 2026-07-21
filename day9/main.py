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