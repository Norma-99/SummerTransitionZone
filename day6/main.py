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