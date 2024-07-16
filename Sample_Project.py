# ci_cd_pipeline.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your_github_token')
ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'your_orchestrator_url')
ORCHESTRATOR_TENANT = os.getenv('ORCHESTRATOR_TENANT', 'your_tenant')
ORCHESTRATOR_USERNAME = os.getenv('ORCHESTRATOR_USERNAME', 'your_username')
ORCHESTRATOR_PASSWORD = os.getenv('ORCHESTRATOR_PASSWORD', 'your_password')

# Function to authenticate to Orchestrator
def orchestrator_authenticate():
    response = requests.post(f'{ORCHESTRATOR_URL}/api/account/authenticate', json={
        'tenancyName': ORCHESTRATOR_TENANT,
        'usernameOrEmailAddress': ORCHESTRATOR_USERNAME,
        'password': ORCHESTRATOR_PASSWORD
    })
    return response.json()['result']

# Function to get package details
def get_package_details(auth_token, package_id):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(f'{ORCHESTRATOR_URL}/odata/Processes({package_id})', headers=headers)
    return response.json()

# Function to upload package to Orchestrator
def upload_package(auth_token, package_path):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        "Content-Type": "application/json"
    }
    with open(package_path, 'rb') as payload:
        files = {'file': payload}
        response = requests.post(f'{ORCHESTRATOR_URL}/odata/Processes/UiPath.Server.Configuration.OData.UploadPackage', headers=headers, files=files)
    return response.json()

# Function to create, update, or delete assets
def manage_assets(auth_token, action, asset_data=None):
    headers = {'Authorization': f'Bearer {auth_token}'}
    if action == "create":
        response = requests.post(f'{ORCHESTRATOR_URL}/odata/Assets', headers=headers, json=asset_data)
    elif action == "update":
        asset_id = asset_data['Id']
        response = requests.put(f'{ORCHESTRATOR_URL}/odata/Assets({asset_id})', headers=headers, json=asset_data)
    elif action == "delete":
        asset_id = asset_data['Id']
        response = requests.delete(f'{ORCHESTRATOR_URL}/odata/Assets({asset_id})', headers=headers)
    return response.json()

# Main function to run the pipeline
def run_pipeline(event_payload):
    auth_token = orchestrator_authenticate()
    
    # Check merge status and update code if needed
    if event_payload['action'] == 'closed' and event_payload['pull_request']['merged']:
        # Download the package from dev Orchestrator
        package_id = 'package_id'  # Replace with actual package ID
        package_details = get_package_details(auth_token, package_id)
        
        # Upload the package to UAT Orchestrator
        package_path = 'path/to/package.zip'  # Replace with actual package path
        upload_package(auth_token, package_path)
        
        # Manage assets
        assets_data = [
            # Fill in with actual assets data
        ]
        for asset in assets_data:
            if asset['change'] == 'add':
                manage_assets(auth_token, 'create', asset)
            elif asset['change'] == 'update':
                manage_assets(auth_token, 'update', asset)
            elif asset['change'] == 'delete':
                manage_assets(auth_token, 'delete', asset)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_payload = request.json
    if event_payload and 'pull_request' in event_payload:
        run_pipeline(event_payload)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "invalid payload"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
