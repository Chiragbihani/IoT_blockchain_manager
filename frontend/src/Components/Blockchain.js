import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Blockchain.css'; // Import the CSS file for styling

const Blockchain = () => {
    const [blocks, setBlocks] = useState([]);
    const centralServerUrl = 'http://127.0.0.1:5000'; // URL of the central server

    // Function to fetch blockchain data
    const fetchBlockchain = async () => {
        try {
            const response = await axios.get(`${centralServerUrl}/blockchain`);
            setBlocks(response.data);
        } catch (error) {
            console.error('Error fetching blockchain:', error);
        }
    };

    // Fetch blockchain data on component mount
    useEffect(() => {
        fetchBlockchain();
    }, []);

    // Handle refresh button click
    const handleRefresh = () => {
        fetchBlockchain(); // Re-fetch the blockchain data
    };

    return (
        <div>
            <div style={{display: "inline-flex", width: "100%", justifyContent: "space-between"}}>
            <h2>Blockchain Commit History</h2>
                <button onClick={handleRefresh} style={{ marginBottom: '10px', float: "right" }}>
                    Refresh Blockchain
                </button>
            </div>
            { blocks.length > 0 ?
            (<div className="block-container">
                {blocks.map((block, index) => (
                    <div className="block" key={index}>
                        <div className="block-data">
                            <strong>Data: </strong> {block.block_data}
                        </div>
                        <br></br>
                        <div className="block-info">
                            <div><strong>Initiated by Node:</strong> {block.committed_by}</div>
                            <div><strong>Commit Time:</strong> {block.commit_time}</div>
                        </div>
                    </div>
                ))}
            </div>) : <p className='no-block'>No Blocks to display, propose a block to commit</p>
            
        }
        </div>
    );
};

export default Blockchain;