import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv("../.env")

# Connect to your storage account
client = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

# Point to the container (drawer inside the filing cabinet)
container_name = "training-logs"
container = client.get_container_client(container_name)

# Create the container if it doesn't exist yet
try:
    container.create_container()
    print(f"Container '{container_name}' created.")
except Exception:
    print(f"Container '{container_name}' already exists, skipping.")

# Upload
with open("garmin_export.csv", "rb") as f:
    container.upload_blob("garmin_export.csv", f, overwrite=True)
    print("Uploaded: garmin_export.csv")

# List all blobs in the container
print("\nFiles in container:")
for blob in container.list_blobs():
    print(f"  - {blob.name}  ({blob.size} bytes)")

# Download and print
print("\nContents of garmin_export.csv:")
data = container.download_blob("garmin_export.csv").readall()
print(data.decode("utf-8"))