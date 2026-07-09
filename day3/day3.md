# Day 3 — "Easiest Chatbot Deploy Ever"
**Concept:** Azure App Service · Deploying a Python web app without Docker
**You build:** A Streamlit chatbot with memory, deployed publicly via App Service.

- [X] Create the `requirements.txt` file with the dependencies needed
- [X] Create an `app.py` file with the code to create a streamlit chatbot

```python
```

- [X] Zip it all in a zip file `zip deploy.zip app.py requirements.txt`
- [X] Tell azure to install dependencies during deploy

```bash
az webapp config appsettings set \
  --name summer-chatbot \
  --resource-group summer-rg \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

```

-[X] Tell azure how to start Streamlit

```bash
az webapp config set \
  --name summer-chatbot \
  --resource-group summer-rg \
  --startup-file "python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0"
\
```

- [X] Add OpenAI key as an app setting since `.env` will not work in the server
```bash
az webapp config appsettings set \
  --name summer-chatbot \
  --resource-group summer-rg \
  --settings AZURE_OPENAI_KEY="$(grep AZURE_OPENAI_KEY ../.env | cut -d'=' -f2)"

```

- [X] To see your webapp config type
```bash
az webapp config appsettings list \
  --name summer-chatbot \
  --resource-group summer-rg \
  --output table
```
- [X] Create the service app plan and the web app
```bash
# Step 1: Create an App Service Plan (the server)
az appservice plan create \
  --name summer-plan \
  --resource-group summer-rg \
  --sku FREE \
  --is-linux \
  --location westeurope

# Step 2: Create the Web App on that plan
az webapp create \
  --name summer-chatbot \
  --resource-group summer-rg \
  --plan summer-plan \
  --runtime "PYTHON:3.11"
```

- [X] Deploy the zip
```bash
# Step 3: Deploy your code (run from your app folder)
az webapp deploy \
  --name summer-chatbot \
  --resource-group summer-rg \
  --src-path . \
  --type zip

```

That's it. Azure reads your `requirements.txt`, installs deps, and serves it.

**What to build:**
```python
# app.py — simple Streamlit chatbot
import streamlit as st
from openai import AzureOpenAI

client = AzureOpenAI(...)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Say something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
```

- [X] To stop the webapp put this command: `az webapp stop --name summer-chatbot --resource-group summer-rg`

- [] To start the webapp put this command: `az webapp start --name summer-chatbot --resource-group summer-rg`

- [] To delete the webapp put these commands: 
```bash
az webapp delete --name summer-chatbot --resource-group summer-rg
az appservice plan delete --name summer-plan --resource-group summer-rg
```