import requests

# URL of the server endpoint
url = 'http://127.0.0.1:5000/receive'

# JSON data to send
json_data = {
    "name": "John Doe",
    "age": 30,
    "city": "New York"
}

# Send POST request with JSON data
response = requests.post(url, json=json_data)

# Print the response from the server
print(f"Response from server: {response.json()}")
