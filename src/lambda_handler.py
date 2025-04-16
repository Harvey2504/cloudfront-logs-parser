import json
from helper.ssm_helper import get_account_details
from providers.azure.azure_provider import create_azure_resources

def lambda_handler(event, context):
    """Lambda function handler."""
    try:
        body = json.loads(event.get('body', '{}'))
        tenant_id = body.get('tenant_id')
        account_id = body.get('account_id')

        if not tenant_id or not account_id:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing tenant_id or account_id.')
            }

        account_details = get_account_details(tenant_id, account_id)

        cloud_provider = account_details.get('cloudprovider')
        region = account_details.get('region')

        # Extract the 'write' block for credentials
        write_data = account_details.get('write', {})

        if cloud_provider == 'aws':
            aws_credentials = {
                'access_key': write_data.get('access_id'),
                'secret_key': write_data.get('access_secret')
            }
            result = create_aws_resources(aws_credentials, region)
        elif cloud_provider == 'azure':
            azure_credentials = {
                'tenant_id': write_data.get('az_tenant_id'),
                'client_id': write_data.get('client_id'),
                'client_secret': write_data.get('client_secret'),
                'subscription_id': write_data.get('subscription_id')
            }
            result = create_azure_resources(azure_credentials, region)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps(f"Unsupported cloud provider: {cloud_provider}")
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Infrastructure creation initiated successfully.',
                'result': result
            })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON in request body.')
        }
    except ValueError as e:
        return {
            'statusCode': 404,
            'body': json.dumps(str(e))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
