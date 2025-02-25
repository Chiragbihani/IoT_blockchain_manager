from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template
from ecdsa import VerifyingKey, NIST256p, BadSignatureError
import logging
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configure CORS for the app
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Configure SocketIO with allowed origins
socketio = SocketIO(app, cors_allowed_origins="*") 
                    # cors_allowed_origins="https://0ac7-2405-201-d02d-48be-20e6-6cdf-2a9d-3440.ngrok-free.app")

# Set up logging with an in-memory log storage
class InMemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.central_logs = [] 
        self.node_logs = {}

    def emit(self, record):
        log_entry = self.format(record)
        log_type = getattr(record, 'log_type', 'central')  # Default to 'central' if log_type is not provided
        node_id = getattr(record, 'node_id', 'unknown')   # Default to 'unknown' if node_id is not provided
        
        # If the log is from a node, store it by node_id
        if log_type == 'node':
            if node_id not in self.node_logs:
                self.node_logs[node_id] = []
            self.node_logs[node_id].append(log_entry)
            socketio.emit('node_log_update', {'node_id': node_id, 'log': log_entry})  # Emit node-specific log
        else:
            # If it's a central log, store it in the central logs
            self.central_logs.append(log_entry)
            socketio.emit('server_log_update', log_entry)  # Emit central server log

    def get_logs(self, node_id=None):
        if node_id:
            return self.node_logs.get(node_id, [])  # Return logs for the specific node
        return {"central_logs": self.central_logs, "node_logs": self.node_logs}  # Return all logs

# Configure logging
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()  # Console output
memory_handler = InMemoryLogHandler()     # In-memory log storage
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
memory_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(memory_handler)

# Global variables
registered_nodes = {}   # node_id: {public_key: public_key_hex, public_url: public_url}
proposal = None         # Stores the block proposal
prepare_messages = {}   # node_id: prepare_message
consensus_messages = {} # node_id: consensus_message
node_logs = {}

@socketio.on('connect')
def handle_connect(auth):
    print("Client connected")
    emit('server_logs', get_all_logs())  # Send all logs when the client connects

# Function to get all stored logs
def get_all_logs():
    return memory_handler.get_logs()

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(get_all_logs())

@socketio.on('request_logs')
def handle_log_request():
    emit('server_logs', get_all_logs())

@app.route('/node_logs', methods=['POST'])
def receive_log():
    try:
        data = request.json
        node_id = data.get("node_id")
        log_message = data.get("log")

        if not node_id or not log_message:
            logger.error("Invalid log data received.", extra={'log_type': 'central'})
            return jsonify({"status": "failed", "message": "Invalid log data."}), 400

        log_type = data.get("log_type", "node")
        log_entry = {"log": log_message, "log_type": log_type}

        if node_id not in node_logs:
            node_logs[node_id] = []
        node_logs[node_id].append(log_entry)

        # Emit the log entry to all connected clients
        socketio.emit('node_log_update', {'node_id': node_id, 'log': log_entry})  # Emit node-specific log

        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error receiving log: {e}", extra={'log_type': 'central'})
        return jsonify({"status": "failed", "message": str(e)}), 500

@app.route('/node_logs/<node_id>', methods=['GET'])
def get_node_logs(node_id):
    # Fetch logs for a specific node
    logs = [log for log in node_logs.get(node_id, []) if log["log_type"] == "node"]
    return jsonify(logs), 200

@app.route('/propose_block', methods=['POST'])
def propose_block():
    global proposal
    block_data = request.json['block_data']
    node_id = request.json['node_id']  # Ensure node_id is included in the log entry
    proposal = {"block_data": block_data, "node_id": node_id}
    logger.info(f"Received block proposal '{block_data}' from Node {node_id}.", 
                extra={'log_type': 'central', 'node_id': node_id})
    logger.info(request.json)
    return jsonify({"status": "received"}), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    node_id = str(request.json['node_id'])
    public_key_hex = request.json['public_key']
    public_url = request.json['public_url']  # Get the public URL from the request
    registered_nodes[node_id] = {
        'public_key': public_key_hex,
        'public_url': public_url
    }
    logger.info(f"Node {node_id}: Registered with server.", 
                extra={'log_type': 'central', 'node_id': node_id})
    logger.info(request.json)
    return jsonify({'node_id': node_id, 'public_key': public_key_hex, 'public_url': public_url}), 201

@app.route('/public_keys', methods=['GET'])
def public_keys():
    return jsonify(registered_nodes), 200

@app.route('/commit_message', methods=['POST'])
def commit_message():
    consensus_message = request.json
    node_id = str(consensus_message['node_id'])
    status = consensus_message['status']
    signature = consensus_message['signature']
    public_key_hex = registered_nodes.get(node_id, {}).get('public_key')

    # Verify the consensus message signature
    if not verify_signature(status, signature, public_key_hex):
        return jsonify({"status": "failed", "message": "Invalid consensus message signature."}), 400

    consensus_messages[node_id] = consensus_message
    logger.info(f"Received consensus message from Node {node_id}.", 
                extra={'log_type': 'central', 'node_id': node_id})
    logger.info(request.json)

    # Check if consensus is reached
    if len(consensus_messages) == len(registered_nodes):
        logger.info("Consensus reached. Committing the block.", 
                    extra={'log_type': 'central'})
        commit_block()
        return jsonify({"status": "success", "message": "Block committed."}), 200
    else:
        return jsonify({"status": "success", "message": "Consensus message received."}), 200

def verify_signature(message, signature_hex, public_key_hex):
    try:
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = VerifyingKey.from_string(public_key_bytes, curve=NIST256p)
        signature_bytes = bytes.fromhex(signature_hex)
        return public_key.verify(signature_bytes, message.encode(), hashfunc=hashlib.sha256)
    except BadSignatureError:
        return False
    except Exception as e:
        logger.error(f"Verification error: {e}", extra={'log_type': 'central'})
        return False

# Function to load the blockchain from a JSON file
def load_blockchain():
    if os.path.exists('blockchain.json'):
        with open('blockchain.json', 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If JSON is invalid, return an empty list
                return []
    return []

# Function to save a new block to the blockchain
def save_block_to_chain(block):
    blockchain = load_blockchain()
    blockchain.append(block)
    with open('blockchain.json', 'w') as f:
        json.dump(blockchain, f, indent=4)

# Modify the commit_block function to save the block with additional information
def commit_block():
    global proposal, prepare_messages, consensus_messages
    logger.info(f"Block data '{proposal['block_data']}' has been committed.", 
                extra={'log_type': 'central'})
    
    # Create a block with additional information
    block = {
        "block_data": proposal['block_data'],
        "committed_by": proposal.get('node_id', 'unknown'),  # Node that initiated the commit
        "commit_time": datetime.now().isoformat(),  # Current date and time in ISO format
    }
    
    # Save the block to the blockchain
    save_block_to_chain(block)  # Save the entire proposal as a block

    # Clear variables for the next consensus round
    proposal = None
    prepare_messages.clear()
    consensus_messages.clear()

# Endpoint to get the blockchain data
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    blockchain = load_blockchain()
    return jsonify(blockchain), 200

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)