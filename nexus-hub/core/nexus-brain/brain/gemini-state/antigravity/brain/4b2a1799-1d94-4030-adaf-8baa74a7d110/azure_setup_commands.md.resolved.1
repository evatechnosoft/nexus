# Azure CLI Commands for IT Inventory OAuth2 Setup

Run these commands in your terminal (with Azure CLI installed and logged in via `az login`).

### 1. Create the App Registration
```bash
appId=$(az ad app create --display-name "IT-Inventory-Watcher" --query appId --output tsv)
echo "Application (Client) ID: $appId"
```

### 2. Create the Service Principal
```bash
az ad sp create --id $appId
```

### 3. Add Microsoft Graph Permissions (Mail.ReadWrite)
# Microsoft Graph Resource ID: 00000003-0000-0000-c000-000000000000
# Mail.ReadWrite (Application) ID: 810c9b0e-f0c9-40d7-a5d5-f178795d1964
```bash
az ad app permission add --id $appId --api 00000003-0000-0000-c000-000000000000 --api-permissions 810c9b0e-f0c9-40d7-a5d5-f178795d1964=Role
```

### 4. Admin Consent (Requires Admin privileges)
```bash
az ad app permission admin-consent --id $appId
```

### 5. Create Client Secret
```bash
secret=$(az ad app credential reset --id $appId --append --query password --output tsv)
echo "Client Secret: $secret"
```

### 6. Get Tenant ID
```bash
tenantId=$(az account show --query tenantId --output tsv)
echo "Tenant ID: $tenantId"
```

---

### Summary of values needed for .env:
- **CLIENT_ID**: Value of $appId
- **TENANT_ID**: Value of $tenantId
- **CLIENT_SECRET**: Value of $secret
