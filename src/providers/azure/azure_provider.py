from azure.identity import ClientSecretCredential
from providers.azure.services.vm import create_virtual_machines
from providers.azure.services.storage import create_storage_accounts
from providers.azure.services.sql import create_sql_servers
from providers.azure.services.disks import create_managed_disks

def create_azure_resources(credentials: dict, region: str):
    try:
        credential = ClientSecretCredential(
            tenant_id=credentials['tenant_id'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret']
        )
        subscription_id = credentials['subscription_id']
    except KeyError as e:
        raise ValueError(f"Missing credential key: {e}") from e
    except Exception as e:
        raise ValueError("Invalid or missing Azure credentials") from e

    create_virtual_machines(credential, subscription_id, region)
    # create_storage_accounts(credential, subscription_id, region)
    # create_sql_servers(credential, subscription_id, region)
    # create_managed_disks(credential, subscription_id, region)
