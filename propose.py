import requests

node_id = 2  # Change to the node you want to propose from
block_data = "Sample block data"
url = f"http://127.0.0.1:{5000 + node_id}/propose_block"
response = requests.post(url, json={"block_data": block_data})
print(response.json())
