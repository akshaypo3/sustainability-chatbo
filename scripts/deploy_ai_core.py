import os
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

def main():
    print("=== SAP AI Core Deployment ===")
    
    # Get environment variables
    auth_url = os.environ.get('AUTH_URL')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    ai_api_url = os.environ.get('AI_API_URL')
    resource_group = os.environ.get('RESOURCE_GROUP', 'default')
    dockerhub_username = os.environ.get('DOCKERHUB_USERNAME')
    
    print(f"Resource Group: {resource_group}")
    print(f"DockerHub Username: {dockerhub_username}")
    
    # Validate required environment variables
    required_vars = ['AUTH_URL', 'CLIENT_ID', 'CLIENT_SECRET', 'AI_API_URL', 'DOCKERHUB_USERNAME']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ Missing required environment variable: {var}")
            exit(1)
    
    try:
        # Create AI Core client
        client = AICoreV2Client(
            base_url=ai_api_url,
            auth_url=auth_url,
            client_id=client_id,
            client_secret=client_secret,
            resource_group=resource_group
        )
        
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
        
        # Create configuration
        print("🚀 Deploying configuration to SAP AI Core...")
        response = client.configuration.create(body=config_data)
        
        print("✅ Configuration deployed successfully!")
        print(f"📋 Configuration ID: {response.id}")
        print(f"📊 Status: {response.status}")
        print(f"🔗 Resource Group: {resource_group}")
        
    except Exception as e:
        print(f"❌ Failed to deploy configuration: {str(e)}")
        
        # Print detailed error information
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"📝 Error details: {e.response.text}")
        elif hasattr(e, 'body'):
            print(f"📝 Error details: {e.body}")
        
        exit(1)

if __name__ == "__main__":
    main()