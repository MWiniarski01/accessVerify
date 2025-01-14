from flask import Flask, request, jsonify
import requests
import logging
import json

# Initialize Flask application
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Function to load configuration from a file
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

# Load configuration from config.json
config = load_config('config/config.json')
ACCESS_VERIFIER_URL = config["ACCESS_VERIFIER_URL"]
FLASK_HOST = config["FLASK_HOST"]
FLASK_PORT = config["FLASK_PORT"]

def verify_access(headers):
    """
    Sends HTTP headers to the AccessVerifier service for validation.
    Args:
        headers (dict): The headers from the incoming client request.
    Returns:
        bool: True if access is granted, False otherwise.
    """
    try:
        # Convert headers dictionary to text/plain format
        headers_str = "\n".join(f"{key}: {value}" for key, value in headers.items())
        
        # Send the headers as text/plain to the AccessVerifier service
        response = requests.post(
            ACCESS_VERIFIER_URL,
            data=headers_str.encode('utf-8'),  # Encode headers to bytes
            headers={'Content-Type': 'text/plain'},
            timeout=10  # Set a timeout for the request
        )
        
        # Log the response status code
        logging.info(f"AccessVerifier response: {response.status_code}")
        
        # Return True if access is granted (HTTP 200)
        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        # Log connection errors or timeouts
        logging.error(f"Error communicating with AccessVerifier: {e}")
        return False

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_request():
    """
    Handles incoming client requests and verifies access using the AccessVerifier service.
    Returns:
        Response: JSON response indicating whether the request was processed or denied.
    """
    if verify_access(request.headers):
        # Access granted, process the request
        return jsonify({'message': 'Request processed'}), 200
    else:
        # Access denied, return an unauthorized response
        return jsonify({'message': 'Access denied'}), 401

if __name__ == '__main__':
    # Start the Flask server with the configured host and port
    app.run(host=FLASK_HOST, port=FLASK_PORT)
