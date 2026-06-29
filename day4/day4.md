# Day 4 — "The File Cabinet"

**Concept:** Azure Blob Storage · Upload · Download · List files
**You build:** A Python script that uploads a training log CSV, reads it back, and lists all files in a container.

---

## The Mental Model First

Before running any commands, understand the 3-layer structure:

```
Storage Account (summerstorage)     ← the filing cabinet itself
  └── Container (training-logs)     ← a drawer inside it
        ├── garmin_export.csv       ← a file (blob)
        └── other_file.txt          ← another blob
```

If you know AWS: **Storage Account = S3**, **Container = S3 bucket**, **Blob = S3 object**. Same idea, different names.

---

## Step 0 - Give the correct permissions
- [X] Enable Microsoft.CognitiveServices: `az provider register --namespace Microsoft.Storage`
- [X] To check if it was registered: `az provider show --namespace Microsoft.Storage --query "registrationState" -o tsv`

## Step 1 — Create the Storage Account

- [X] Run this command to create your storage account:

```bash
az storage account create \
  --name summerstorage2026 \
  --resource-group summer-rg \
  --location westeurope \
  --sku Standard_LRS
```

| Part | What it means |
|---|---|
| `az storage account create` | "Create a new file cabinet on Azure" |
| `--name summerstorage2026` | Name it `summerstorage` — must be globally unique, lowercase only, no dashes |
| `--resource-group summer-rg` | Put it in your existing `summer-rg` folder |
| `--location westeurope` | Host it in the Netherlands datacenter |
| `--sku Standard_LRS` | Standard tier, data replicated 3× in the same datacenter (LRS = Locally Redundant Storage) |

---

## Step 2 — Get the Connection String

This is how Python authenticates to your storage account. Think of it as an API key, but for storage.

- [X] Run this to get your connection string:

```bash
az storage account show-connection-string \
  --name summerstorage2026 \
  --resource-group summer-rg \
  --output tsv
```

You'll get a long string starting with `DefaultEndpointsProtocol=https;AccountName=summerstorage;...`

- [X] Copy it and add it to your root `.env` file (the same one with your OpenAI key):

```
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=summerstorage;...
```

---

## Step 3 — Install the Python SDK

- [X] Install the Azure Blob Storage library:

```bash
pip3.11 install azure-storage-blob
```

(`python-dotenv` is already installed from Day 2.)

---

## Step 4 — Create a Sample CSV to Upload

- [X] Create `day4/garmin_export.csv` with this content:

```
date,activity,distance_km,duration_min,avg_hr
2026-06-01,Run,10.2,55,148
2026-06-03,Bike,42.0,75,135
2026-06-05,Swim,2.5,48,140
2026-06-07,Run,15.0,82,152
2026-06-09,Bike,60.0,95,138
```

This is a fake Garmin training export — the file you'll upload to Azure.

---

## Step 5 — Write the Python Script

- [X] Create `day4/main.py`:

```python
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
```

---

## Step 6 — Run It

- [X] Run the script from inside the `day4/` folder:

```bash
cd day4
python main.py
```

Expected output:
```
Container 'training-logs' created.
Uploaded: garmin_export.csv

Files in container:
  - garmin_export.csv  (156 bytes)

Contents of garmin_export.csv:
date,activity,distance_km,duration_min,avg_hr
2026-06-01,Run,10.2,55,148
2026-06-03,Bike,42.0,75,135
2026-06-05,Swim,2.5,48,140
2026-06-07,Run,15.0,82,152
2026-06-09,Bike,60.0,95,138
```

---

## Optional: Verify in the Azure Portal

- [X] Go to [portal.azure.com](https://portal.azure.com)
- Search for **Storage accounts** → click `summerstorage2026`
- Click **Containers** → `training-logs`
- You should see `garmin_export.csv` — you can even download it directly from the browser

---

## Mental Model

```
Your laptop                  Azure Blob Storage
───────────                  ────────────────────────────────────────
garmin_export.csv  →→→  summerstorage / training-logs / garmin_export.csv
                   ←←←  (download back anytime, from anywhere)
```

This is the same pattern companies use to store logs, ML model weights, training datasets, and exports from pipelines. The Python code you wrote here is production-grade — this is exactly what a data engineer would write.

---

## ✅ Done when:

- [X] Script runs without errors
- [X] You can see the file listed in the output
- [X] You can see it in the Azure portal too
- [X] You understand: **Storage Account → Container → Blob**
