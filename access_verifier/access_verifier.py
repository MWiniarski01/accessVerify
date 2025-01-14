from flask import Flask, request, jsonify
import requests
import threading
import logging
import ipaddress
from datetime import datetime, timedelta
import json

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

config = load_config('config/config.json')

#ENV

# URL to fetch the IP list for the AWS Europe West region
AWS_IP_RANGES_URL = config["AWS_IP_RANGES_URL"]
LOCAL_IP_RANGE = config["LOCAL_IP_RANGE"]

# The region we are interested in
TARGET_REGION = config["TARGET_REGION"]

FLASK_HOST = config["FLASK_HOST"]
FLASK_PORT = config["FLASK_PORT"]


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global list of allowed IP addresses
allowed_ips = set()
lock = threading.Lock()

def update_allowed_ips():
    """Updates the list of allowed IP addresses."""
    global allowed_ips
    logging.info("Starting to update the list of allowed IPs...")
    try:
        response = requests.get(AWS_IP_RANGES_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Filter IP addresses for the eu-west-1 region
        new_ips = {
            ip_range["ip_prefix"]
            for ip_range in data.get("prefixes", [])
            if ip_range.get("region") == TARGET_REGION
        }
        
        # Safe update of the list
        with lock:
            if LOCAL_IP_RANGE: 
                allowed_ips = new_ips.union({LOCAL_IP_RANGE}) 
            else:
                allowed_ips = new_ips
        
        logging.info(f"Updated the list of allowed IPs: {allowed_ips}")
    except Exception as e:
        logging.error(f"Error updating IP addresses: {e}")

def is_ip_allowed(client_ip):
    """Checks if the IP address is within the allowed ranges."""
    try:
        ip_obj = ipaddress.ip_address(client_ip)  # Create an IP object

        # Check if the address is within one of the allowed ranges
        for ip_range in allowed_ips:
            if ip_obj in ipaddress.ip_network(ip_range, strict=False):
                return True
    except ValueError as e:
        logging.error("Invalid IP address: %s", client_ip)
    return False


# Set the update schedule every 24h
def schedule_ip_updates():
    """Schedules the IP update function."""
    threading.Timer(24 * 3600, schedule_ip_updates).start()
    update_allowed_ips()

@app.route("/verify", methods=["POST"])
def verify():
    """Verifies access based on the submitted HTTP headers."""
    try:
        # Read the data sent as text/plain
        headers_raw = request.data.decode('utf-8')

        # Convert text/plain data to a headers dictionary
        headers = {}
        for line in headers_raw.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        # Get the client's IP address from the headers (e.g., X-Forwarded-For)
        client_ip = headers.get("X-Forwarded-For", request.remote_addr)

        # Verify the IP address
        with lock:
            if is_ip_allowed(client_ip):
                logging.info("Access allowed: %s", client_ip)
                return jsonify({"status": "allowed"}), 200
            else:
                logging.warning("Access denied: %s", client_ip)
                return jsonify({"status": "unauthorized"}), 401

    except Exception as e:
        logging.error("Error during verification: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Initial refresh of IP addresses
    update_allowed_ips()
    # Start the scheduler
    schedule_ip_updates()
    # Start the Flask server
    app.run(FLASK_HOST, FLASK_PORT)