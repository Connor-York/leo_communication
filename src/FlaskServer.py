from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to receive JSON data
@app.route('/receive', methods=['POST'])
def receive_json():
    data = request.get_json()  # Get the JSON data from the request
    print(f"Received JSON: {data}")

    # Send a response back
    response = {"message": "JSON received successfully!", "data_received": data}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
