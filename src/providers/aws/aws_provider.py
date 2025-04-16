def create_aws_resources(credentials, region):
    """Print AWS credentials and region."""
    print("Received AWS Credentials:")
    print(f"Access Key: {credentials['access_key']}")
    print(f"Secret Key: {credentials['secret_key']}")
    print(f"Region: {region}")
