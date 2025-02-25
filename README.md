# IoT Security Using PBFT and ECC

## Overview
This project enhances the security of Internet of Things (IoT) networks by integrating **Practical Byzantine Fault Tolerance (PBFT) consensus** with **Elliptic Curve Cryptography (ECC)**. The solution ensures **secure, scalable, and efficient** communication among resource-constrained IoT devices while maintaining authentication, data integrity, and fault tolerance without relying on centralized servers.

## Features
- **Decentralized Authentication:** Uses ECC and ECDSA for lightweight and secure authentication.
- **Fault-Tolerant Consensus:** Implements PBFT to validate transactions and ensure tamper resistance.
- **Blockchain Integration:** Maintains a decentralized, immutable ledger for enhanced security.
- **Flask-based REST API:** Facilitates seamless communication and public key synchronization.
- **Dynamic Key Synchronization:** Periodic key updates enhance security.
- **Scalability:** Modular architecture allows easy expansion.

## Project Structure
```
├── backend/             # Core backend logic
│   ├── app.py          # Flask-based API
│   ├── pbft.py         # PBFT consensus implementation
│   ├── ecc.py          # ECC authentication & encryption
│   ├── blockchain.py   # Blockchain for transaction logging
│   ├── config.py       # Configuration settings
│   ├── database/       # Database integration
│   ├── tests/          # Unit tests for security & performance
├── docs/               # Project documentation
├── README.md           # Project overview
```

## Technologies Used
- **Programming Language:** Python
- **Framework:** Flask (for REST API)
- **Cryptography:** ECC with ECDSA
- **Consensus Algorithm:** PBFT
- **Database:** SQLite / PostgreSQL
- **Blockchain:** Custom ledger implementation

## Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/iot-security-pbft-ecc.git
   cd iot-security-pbft-ecc
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Flask API:**
   ```bash
   python backend/app.py
   ```
5. **Test the setup:**
   ```bash
   pytest backend/tests/
   ```

## API Endpoints
| Method | Endpoint             | Description                    |
|--------|----------------------|--------------------------------|
| POST   | `/register`          | Register a new IoT node       |
| POST   | `/authenticate`      | Authenticate node with ECC    |
| GET    | `/consensus`         | Trigger PBFT consensus        |
| GET    | `/blockchain`        | Retrieve transaction history  |

## Screenshots of the Dashboard
![image](https://github.com/user-attachments/assets/9687fce8-6ffa-423f-b59b-e17b5e00040f)
![image](https://github.com/user-attachments/assets/6000c2ce-fef1-49c1-9e75-ece4d15b89e4)
![image](https://github.com/user-attachments/assets/67202af8-6c37-4111-a8eb-d99da3b42583)


## Future Improvements
- Integrate AI-based anomaly detection.
- Enhance scalability for large-scale IoT networks.
- Implement cross-platform interoperability.

## License
This project is licensed under the **MIT License**.

---
**For more details, refer to the documentation in the `docs/` directory.**

