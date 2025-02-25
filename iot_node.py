from flask_cors import CORS
import requests
from ecdsa import SigningKey, VerifyingKey, NIST256p, BadSignatureError
import hashlib
import os
import sys
import threading
import time
from flask import Flask, request, jsonify

block_data = ""

class IoTNode:
    def __init__(self, node_id, central_server_url):
        self.node_id = node_id
        self.central_server_url = central_server_url
        self.public_url = self.get_ngrok_url()
        self.key_file = f"node_{self.node_id}_key.pem"
        self.load_or_generate_keys()
        self.public_keys = {}  # Store public keys of other nodes
        self.public_urls = {}  # Store public URLs of other nodes
        self.app = Flask(__name__)
        CORS(self.app, origins="*")
        self.setup_routes()
        self.received_proposal = None
        self.prepare_messages = {}
        self.consensus_reached = False
        self.is_primary = False
        self.current_primary_id = None

    def get_ngrok_url(self):
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        public_url = data['tunnels'][0]['public_url']
        return public_url

    def log_message(self, message, log_type='node'):
        log_data = {
            "node_id": self.node_id,
            "log": message,
            "log_type": log_type
        }
        try:
            response = requests.post(f"{self.central_server_url}/node_logs", json=log_data)
            if response.status_code == 200:
                print(f"Node {self.node_id}: Log sent successfully.")
            else:
                print(f"Node {self.node_id}: Failed to send log. Status code: {response.status_code}")
        except Exception as e:
            print(f"Node {self.node_id}: Error sending log: {e}")

    def load_or_generate_keys(self):
        if os.path.exists(self.key_file):
            # Load existing key
            with open(self.key_file, 'rb') as f:
                self.private_key = SigningKey.from_pem(f.read())
            self.public_key = self.private_key.verifying_key
            self.log_message(f"Loaded existing key pair.", log_type='node')
        else:
            # Generate new key
            self.private_key = SigningKey.generate(curve=NIST256p)
            self.public_key = self.private_key.verifying_key
            # Save the key to a file
            with open(self.key_file, 'wb') as f:
                f.write(self.private_key.to_pem())
            self.log_message(f"Generated new key pair.", log_type='node')

    def setup_routes(self):
        @self.app.route('/receive_proposal', methods=['POST'])
        def receive_proposal():
            proposal = request.json
            primary_node_id = str(proposal["node_id"])
            block_data = proposal["block_data"]
            signature = proposal["signature"]
            message = f"{primary_node_id}:{block_data}"
            primary_public_key_hex = self.public_keys.get(primary_node_id)
            if self.verify_signature(message, signature, primary_public_key_hex):
                self.log_message(f"Verified primary's proposal.", log_type='node')
                self.received_proposal = proposal
                self.current_primary_id = primary_node_id  # Set the current primary
                self.send_prepare()
            else:
                self.log_message(f"Failed to verify primary's proposal.", log_type='node')
            return jsonify({"status": "received"}), 200

        @self.app.route('/receive_prepare', methods=['POST'])
        def receive_prepare():
            prepare_message = request.json
            node_id = str(prepare_message['node_id'])
            signature = prepare_message['signature']
            public_key_hex = self.public_keys.get(node_id)
            if self.verify_signature("prepared", signature, public_key_hex):
                print(f"Node {self.node_id}: Received prepare message from Node {node_id}.")
                self.prepare_messages[node_id] = prepare_message
                if len(self.prepare_messages) >= len(self.public_keys) - 1:
                    print(f"Node {self.node_id}: Received all prepare messages.")
                    self.send_consensus()
            else:
                print(f"Node {self.node_id}: Invalid prepare message from Node {node_id}.")
            return jsonify({"status": "received"}), 200

        @self.app.route('/propose_block', methods=['POST'])
        def propose_block():
            # Allow any node to propose a block
            block_data = request.json.get('block_data')
            if block_data:
                self.is_primary = True
                self.current_primary_id = str(self.node_id)
                self.pre_prepare(block_data)
                self.log_message(f"Block proposal initiated.", log_type='node')
                return jsonify({"status": "success", "message": "Block proposal initiated."}), 200
            else:
                self.log_message(f"Block data is missing.", log_type='node')
                return jsonify({"status": "failed", "message": "Block data is missing."}), 400
        @self.app.route('/status', methods=['GET'])
        def check_status():
            self.log_message("Status: Running", log_type='node')
            return jsonify({"Status:" : "Running"}), 200

    def run(self):
        # Start the Flask app in a separate thread
        threading.Thread(target=lambda: self.app.run(port=5000, debug=False, use_reloader=False)).start()
        time.sleep(1)  # Wait for the server to start
        self.register_node()
        self.get_public_keys()
        # Start the public key update thread
        threading.Thread(target=self.update_public_keys_periodically, daemon=True).start()
        # Keep the node running
        while True:
            time.sleep(1)

    def update_public_keys_periodically(self):
        while True:
            self.get_public_keys()
            time.sleep(5)  # Fetch public keys every 5 seconds

    def register_node(self):
        public_key_hex = self.public_key.to_string().hex()
        response = requests.post(f"{self.central_server_url}/register_node", json={
            "node_id": self.node_id,
            "public_key": public_key_hex,
            "public_url": self.public_url  # Include the public URL in the registration
        })
        if response.status_code == 201:
            print(f"Node {self.node_id}: Registered with server.")
        else:
            print(f"Node {self.node_id}: Registration failed.")
            print(response.text)

    def get_public_keys(self):
        response = requests.get(f"{self.central_server_url}/public_keys")
        if response.status_code == 200:
            data = response.json()
            new_public_keys = {k: v['public_key'] for k, v in data.items()}
            new_public_urls = {k: v['public_url'] for k, v in data.items()}
            if new_public_keys != self.public_keys or new_public_urls != self.public_urls:
                self.public_keys = new_public_keys
                self.public_urls = new_public_urls
                print(f"Node {self.node_id}: Updated public keys and URLs.")
        else:
            print(f"Node {self.node_id}: Failed to get public keys.")

    def sign_message(self, message):
        signature = self.private_key.sign(message.encode(), hashfunc=hashlib.sha256)
        return signature.hex()
    

    def send_consensus(self):
        consensus_message = {
                "node_id": self.node_id,
                "status": "commit",
                "signature": self.sign_message("commit")
            }
        self.log_message(f"Sending consensus message: {consensus_message}", log_type='node')
        response = requests.post(f"{self.central_server_url}/commit_message", json=consensus_message)
        if response.status_code == 200:
                self.log_message(f"Sent consensus message to server.", log_type='node')
        else:
                self.log_message(f"Failed to send consensus message to server. Status code: {response.status_code}", log_type='node')
        self.consensus_reached = True

    def verify_signature(self, message, signature_hex, public_key_hex):
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = VerifyingKey.from_string(public_key_bytes, curve=NIST256p)
            signature_bytes = bytes.fromhex(signature_hex)
            return public_key.verify(signature_bytes, message.encode(), hashfunc=hashlib.sha256)
        except (BadSignatureError, ValueError, TypeError) as e:
            print(f"Node {self.node_id}: Verification error: {e}")
            return False

    def pre_prepare(self, block_data):
        # Primary node signs the block and sends it to all replicas
        message = f"{self.node_id}:{block_data}"
        signature = self.sign_message(message)
        proposal = {
            "node_id": self.node_id,
            "block_data": block_data,
            "signature": signature
        }
        # Send proposal to central server
        response = requests.post(f"{self.central_server_url}/propose_block", json=proposal)
        # Send proposal to all replicas
        for node_id, public_url in self.public_urls.items():
            if node_id != str(self.node_id):
                try:
                    response = requests.post(f"{public_url}/receive_proposal", json=proposal)
                    if response.status_code == 200:
                        print(f"Node {self.node_id}: Sent proposal to Node {node_id}.")
                    else:
                        print(f"Node {self.node_id}: Failed to send proposal to Node {node_id}.")
                except Exception as e:
                    print(f"Node {self.node_id}: Error sending proposal to Node {node_id}: {e}")

    def send_prepare(self):
        # Send prepare message back to primary
        prepare_message = {
            "node_id": self.node_id,
            "status": "prepared",
            "signature": self.sign_message("prepared")
        }
        primary_url = self.public_urls[self.current_primary_id]
        try:
            response = requests.post(f"{primary_url}/receive_prepare", json=prepare_message)
            if response.status_code == 200:
                print(f"Node {self.node_id}: Sent prepare message to primary.")
                self.send_consensus()
            else:
                print(f"Node {self.node_id}: Failed to send prepare message to primary.")
        except Exception as e:
            print(f"Node {self.node_id}: Error sending prepare message to primary: {e}")

    

if __name__ == '__main__':
        node_id = int(sys.argv[1])
        central_server_url = "https://326d-2405-201-5c13-f073-dde-8857-ce93-d66e.ngrok-free.app"
        node = IoTNode(node_id=node_id, central_server_url=central_server_url)
        node.run()