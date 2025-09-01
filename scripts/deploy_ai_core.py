import os
import requests
import json

def main():
    print("=== SAP AI Core Deployment (Direct API) ===")
    
    # Get environment variables
    auth_url = os.environ.get('AUTH_URL')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    ai_api_url = os.environ.get('AI_API_URL')
    resource_group = os.environ.get('RESOURCE_GROUP', 'default')
    dockerhub_username = os.environ.get('DOCKERHUB_USERNAME')
    
    print(f"Resource Group: {resource_group}")
    
    # Get access token
    token_response = requests.post(
        auth_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if token_response.status_code != 200:
        print(f"❌ Failed to get access token: {token_response.text}")
        exit(1)
    
    access_token = token_response.json()['access_token']
    
    # Configuration data
    config_data = {
        "apiVersion": "ai.sap.com/v1alpha1",
        "kind": "Configuration",
        "metadata": {
            "name": "sustainability-chatbot-config",
            "annotations": {
                "scenarios.ai.sap.com/name": "sustainability-chatbot-scenario",
                "executables.ai.sap.com/name": "sustainability-chatbot-executable"
            },
            "labels": {
                "ai.sap.com/resourceGroup": resource_group
            }
        },
        "spec": {
            "template": {
                "name": "sustainability-chatbot-serving"
            },
            "inputs": {
                "parameters": [
                    {
                        "name": "image",
                        "value": f"docker.io/{dockerhub_username}/sustainability-chatbot:latest"
                    },
                    {
                        "name": "resourceGroup",
                        "value": resource_group
                    }
                ]
            }
        }
    }
    
    # Create configuration via direct API call
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/yaml',
        'AI-Resource-Group': resource_group
    }
    
    url = f"{ai_api_url}/v2/lm/configurations?resourceGroup={resource_group}"
    
    print("🚀 Deploying configuration to SAP AI Core...")
    response = requests.post(url, headers=headers, data=json.dumps(config_data))
    
    if response.status_code in [200, 201]:
        print("✅ Configuration deployed successfully!")
        print(f"📋 Response: {response.text}")
    else:
        print(f"❌ Failed to deploy configuration. Status: {response.status_code}")
        print(f"📝 Error details: {response.text}")
        exit(1)

if __name__ == "__main__":
    main()