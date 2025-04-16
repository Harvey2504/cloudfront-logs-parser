import boto3
import json

def get_account_details(tenant_id, account_id):
    """Fetch and parse all account details from SSM Parameter Store."""
    ssm_client = boto3.client('ssm')
    parameter_name = f"/pccm-rs/dev/{tenant_id}"

    try:
        # Retrieve the parameter from SSM
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        param_value = json.loads(response['Parameter']['Value'])

        # Navigate to the specific account data
        account_data = param_value.get('cds', {}).get(account_id)

        if not account_data:
            raise KeyError(f"Account ID {account_id} not found.")

        # Return the entire account data
        return account_data

    except ssm_client.exceptions.ParameterNotFound:
        raise ValueError(f"Parameter {parameter_name} not found.")
    except Exception as e:
        raise RuntimeError(f"Error retrieving or parsing parameter: {str(e)}")
