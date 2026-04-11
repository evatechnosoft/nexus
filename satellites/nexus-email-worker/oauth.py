import msal
import os
import logging

log = logging.getLogger(__name__)


def get_ms_token():
    """
    Azure AD (Microsoft Entra ID) üzerinden Client Credentials Flow ile access token alır.
    """
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([client_id, tenant_id, client_secret]):
        log.warning("OAuth2 için gerekli AZURE_ ayarları eksik.")
        return None

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    # Exchange Online (EWS) için gerekli scope
    scopes = ["https://outlook.office365.com/.default"]

    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        log.error(
            "Token alınamadı: %s", result.get("error_description", result.get("error"))
        )
        return None
