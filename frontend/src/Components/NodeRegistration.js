import React, { useState } from 'react';
import axios from 'axios';

function NodeRegistration() {
  const [nodeId, setNodeId] = useState('');
  const [generatedKeys, setGeneratedKeys] = useState(null);

  const registerNode = async () => {
    if (!nodeId) {
      alert('Please provide Node ID.');
      return;
    }
    try {
      const response = await axios.post('http://127.0.0.1:8000/register_node', {
        node_id: nodeId,
      });
      setGeneratedKeys(response.data);
      alert('Node Registered: ' + response.data.node_id);
    } catch (error) {
      console.error('Error registering node:', error);
      alert('Failed to register node');
    }
  };

  return (
    <div className="card">
      <div className="card-header">Register New Node</div>
      <div className="card-body">
        <input
          type="text"
          placeholder="Node ID"
          value={nodeId}
          onChange={(e) => setNodeId(e.target.value)}
        />
        <button onClick={registerNode} style={{ marginTop: '10px' }}>
          Register Node
        </button>
        {generatedKeys && (
          <div style={{ marginTop: '20px' }}>
            <h5>Generated Keys</h5>
            <p><strong>Public Key:</strong> {generatedKeys.public_key}</p>
            <p><strong>Private Key:</strong> {generatedKeys.private_key}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default NodeRegistration;