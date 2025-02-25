import React, { useEffect, useState } from "react";
import axios from "axios";

const RegisteredNodes = () => {
  const [nodes, setNodes] = useState({});
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(false); // State to track loading status

  // URL of the central server
  const centralServerUrl = 'http://127.0.0.1:5000';

  // Function to fetch registered nodes
  const fetchNodes = async () => {
    setLoading(true); // Set loading to true when fetching starts
    try {
      const response = await axios.get(`${centralServerUrl}/public_keys`);
      setNodes(response.data); // Store the nodes as an object
      console.log(typeof(response.data));
      console.log(nodes);
    } catch (error) {
      console.error("Error fetching registered nodes:", error);
    } finally {
      setLoading(false); // Set loading to false after fetching is complete
    }
  };

  // Fetch nodes when the component mounts
  useEffect(() => {
    fetchNodes();
  }, []);

  // Function to check the status of each node
  useEffect(() => {
    const checkNodeStatus = async () => {
      const newStatus = {};
      for (const [nodeId, nodeData] of Object.entries(nodes)) {
        try {
          await axios.get(`${nodeData.public_url}/status`); // Use the public URL of the node
          newStatus[nodeId] = "Running";
        } catch (error) {
          newStatus[nodeId] = "Stopped";
        }
      }
      setStatus(newStatus);
    };

    if (Object.keys(nodes).length > 0) {
      checkNodeStatus();
    }
  }, [nodes]);

  return (
    <div style={{ "marginBottom": "20px" }}>

      <div style={{ display: "inline-flex", width: "100%", justifyContent: "space-between" }}>
        <h2>Node Status</h2>
        {/* Refresh Button */}
        <button
          onClick={fetchNodes}
          style={{
            float: "right",
            marginBottom: "20px",
            padding: "10px 15px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          Refresh Node List
        </button>

      </div>


      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          marginBottom: "20px",
        }}
      >
        <thead>
          <tr>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Node ID</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Public Key</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Public URL</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Status</th>
          </tr>
        </thead>
        {
          Object.keys(nodes).length > 0 ?
        
        (<tbody>
          {loading ? (
            <tr>
              <td colSpan="4" style={{ textAlign: "center", padding: "20px", fontSize: "18px" }}>
                Loading...
              </td>
            </tr>
          ) : (
            Object.entries(nodes).map(([nodeId, {public_key, public_url}]) => (
              <tr key={nodeId}>
                <td style={{ maxWidth: "100px" ,border: "1px solid #ccc", padding: "10px" }}>{nodeId}</td>
                <td style={{ border: "1px solid #ccc", padding: "10px" }}>{public_key.slice(0, 30) + "...."}</td>
                <td style={{ border: "1px solid #ccc", padding: "10px" }}>{public_url}</td>
                <td style={{ border: "1px solid #ccc", padding: "10px" }}>
                  {status[nodeId] || "Checking..."}
                </td>
              </tr>
            ))
          )}
        </tbody>) :
        <td colSpan={4}>
          <p style={{height: "200px", display: "flex", "justifyContent" : "center", "alignItems": "center", "backgroundColor": "#ededed"}}>No Nodes to display</p>
        </td>

        }
      </table>
    </div>
  );
};

export default RegisteredNodes;
