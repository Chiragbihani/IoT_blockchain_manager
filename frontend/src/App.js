import React from 'react';
// import NodeRegistration from './Components/NodeRegistration';
import RegisteredNodes from './Components/NodeStatus';
import Logs from './Components/Logs';
import Blockchain from './Components/Blockchain';
import BlockProposal from './Components/BlockProposal';
// import ConsensusVisualization from './Components/ConsensusVisualization';
import './App.css'


function App() {
  return (
    <div className="container">
      <h1>IoT Dashboard</h1>
      <div className="section">
        <Blockchain/>
      </div>
      <div className="section">
        <BlockProposal />
      </div>
      <div className="section">
        <RegisteredNodes/>
        <Logs/>
      </div>

    </div>
  );
}


export default App;