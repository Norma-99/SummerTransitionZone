# Day 1: Hello World App

After setting up your account, creating a zero-spend budget and looking through the materials these are the steps I followed to create a Hello World web page: 

## Core exercises

- [X] Open a Terminal in VSCode and go to your project folder.
- [X] Install Azure CLI: `brew install azure-cli`
- [X] Check its properly installed: `az --version`
- [X] Log In into Azure `az login` 
- [X] Enable Microsoft Web: `az provider register --namespace Microsoft.Web`
- [X] To check if it was registered: `az provider show --namespace Microsoft.Web --query "registrationState" -o tsv`
- [X] Run the command to create a webpage: `az group create --name summer-rg --location westeurope`
- [X] Run the command to deploy the static web page: `az staticwebapp create --name my-first-azure-app --resource-group summer-rg`
- [X] Get the url by adding the `defaultHostname` to `https://`. So `https://<defaultHostname>`


## ⚠️ EXTRA: One Thing to Know Before You Run That Last Command

`az staticwebapp create` on its own creates an **empty** Static Web App — there's no website content yet. To actually see something live, you need one more step. Here's the simplest path:

```bash
# 1. Create a tiny project folder with one HTML file, in our case day1 folder
echo "<h1>Hello, I'm learning Azure ☀️</h1>" > index.html

# 2. Install the Static Web Apps CLI (one-time)
npm install -g @azure/static-web-apps-cli

# 3. Get the deployment token for the app you just created
az staticwebapp secrets list \
  --name my-first-azure-app \
  --resource-group summer-rg \
  --query "properties.apiKey" -o tsv

# This prints a long token string — copy it

# 4. Deploy your index.html using that token
swa deploy . --deployment-token PASTE_TOKEN_HERE --env production
```

The terminal will print a live URL at the end — something like `https://my-first-azure-app.azurestaticapps.net`. Open it in your browser.

## Undeploy: To cleanly remove the app

**Option 1: Delete the Static Web App**
```bash
az staticwebapp delete \
  --name HelloWorldApp \
  --resource-group summer-rg \
  --yes
```

**Option 2: Delete the whole recource group**

```bash
az group delete --name summer-rg --yes --no-wait
```

**Option 3: Only delete the site content**

```bash
mkdir -p /tmp/empty-swa
swa deploy /tmp/empty-swa --deployment-token <token> --env production
```