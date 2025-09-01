import os
import requests
import json

def main():
    print("=== FINAL SAP AI Core Deployment ===")
    
    # Get environment variables
    auth_url = os.environ.get('AUTH_URL')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    ai_api_url = os.environ.get('AI_API_URL')
    resource_group = os.environ.get('RESOURCE_GROUP', 'default')
    dockerhub_username = os.environ.get('DOCKERHUB_USERNAME')
    
    print(f"Resource Group: {resource_group}")
    print(f"DockerHub Username: {dockerhub_username}")
    print(f"AI API URL: {ai_api_url}")
    
    # Get access token
    try:
        print("1. Getting access token...")
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
            print(f"❌ Token failed: {token_response.status_code} - {token_response.text}")
            exit(1)
        
        access_token = token_response.json()['access_token']
        print("✅ Access token obtained")
        
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        exit(1)
    
    # Configuration data in EXACT format SAP AI Core expects
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
    
    # Make the API call with EXACT headers SAP expects
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'AI-Resource-Group': resource_group
    }
    
    # Use the EXACT endpoint format
    url = f"{ai_api_url}/v2/lm/configurations"
    
    print("2. Deploying configuration...")
    print(f"   URL: {url}")
    print(f"   Headers: {headers}")
    
    try:
        # Add resource group as query parameter (SAP specific)
        params = {'resourceGroup': resource_group}
        
        response = requests.post(
            url, 
            headers=headers, 
            params=params,
            json=config_data
        )
        
        print(f"3. Response: HTTP {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS: Configuration deployed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Debug: Check what permissions you actually have
            print("\n4. Debug: Checking your roles...")
            roles_url = f"{ai_api_url}/v2/admin/roleAssignments"
            roles_response = requests.get(roles_url, headers=headers)
            
            if roles_response.status_code == 200:
                roles = roles_response.json()
                print("   Your roles:")
                for role in roles:
                    print(f"     - {role.get('roleName')} (RG: {role.get('resourceGroup')})")
            else:
                print(f"   Cannot check roles: {roles_response.status_code}")
            
            exit(1)
            
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()