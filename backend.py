import os
import requests
from flask import Flask, request, jsonify

# --- Configuration ---
# Your specific Backendless API endpoint for the 'users1' table.
BACKENDLESS_API_URL = "https://strongquestion-us.backendless.app/api/data/users1"

app = Flask(__name__)

# Helper function to generate a clean response from the Backendless result
def backendless_response(response):
    """
    Standardizes the response handling from the Backendless API.
    """
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        # Handle cases where the response is not valid JSON (e.g., successful DELETE returns 200/204 with no body)
        return jsonify({"message": response.text or "Operation successful"}), response.status_code

    if response.ok:
        return jsonify(data), response.status_code
    else:
        # Backendless error structure usually includes a 'message' or 'code'
        error_message = data.get("message", "An unexpected Backendless error occurred.")
        return jsonify({"error": error_message, "details": data}), response.status_code

# 1. READ ALL USERS (GET /users1)
@app.route('/users', methods=['GET'])
def get_all_users():
    """
    Retrieves all user records from the Backendless 'users1' table.
    """
    app.logger.info(f"Attempting to GET all users from: {BACKENDLESS_API_URL}")
    try:
        response = requests.get(BACKENDLESS_API_URL)
        return backendless_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network or API connectivity error: {e}")
        return jsonify({"error": "Failed to connect to Backendless API", "details": str(e)}), 503

# 2. CREATE A NEW USER (POST /users1)
@app.route('/users', methods=['POST'])
def create_user():
    """
    Creates a new user record in the Backendless 'users1' table.
    Requires 'nombre' and 'email' in the JSON body.
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')

    if not nombre or not email:
        return jsonify({"error": "Missing required fields: 'nombre' and 'email'"}), 400

    # Backendless expects the data object
    payload = {'nombre': nombre, 'email': email}

    app.logger.info(f"Attempting to POST new user to: {BACKENDLESS_API_URL} with data: {payload}")
    try:
        response = requests.post(BACKENDLESS_API_URL, json=payload)
        return backendless_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network or API connectivity error: {e}")
        return jsonify({"error": "Failed to connect to Backendless API", "details": str(e)}), 503

# 3. READ ONE USER BY ID (GET /users1/<object_id>)
@app.route('/users/<string:object_id>', methods=['GET'])
def get_user(object_id):
    """
    Retrieves a single user record by its Backendless objectId.
    """
    user_url = f"{BACKENDLESS_API_URL}/{object_id}"
    app.logger.info(f"Attempting to GET user with ID {object_id} from: {user_url}")
    try:
        response = requests.get(user_url)
        return backendless_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network or API connectivity error: {e}")
        return jsonify({"error": "Failed to connect to Backendless API", "details": str(e)}), 503

# 4. UPDATE A USER (PUT /users1/<object_id>)
@app.route('/users/<string:object_id>', methods=['PUT'])
def update_user(object_id):
    """
    Updates an existing user record by its Backendless objectId.
    Accepts 'nombre' and/or 'email' in the JSON body.
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    user_url = f"{BACKENDLESS_API_URL}/{object_id}"

    # Only send fields that are present in the request body
    payload = {}
    if 'nombre' in data:
        payload['nombre'] = data['nombre']
    if 'email' in data:
        payload['email'] = data['email']

    if not payload:
        return jsonify({"error": "No valid fields provided for update ('nombre' or 'email')"}), 400

    app.logger.info(f"Attempting to PUT update to user {object_id} at: {user_url} with data: {payload}")
    try:
        response = requests.put(user_url, json=payload)
        return backendless_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network or API connectivity error: {e}")
        return jsonify({"error": "Failed to connect to Backendless API", "details": str(e)}), 503

# 5. DELETE A USER (DELETE /users1/<object_id>)
@app.route('/users/<string:object_id>', methods=['DELETE'])
def delete_user(object_id):
    """
    Deletes a single user record by its Backendless objectId.
    """
    user_url = f"{BACKENDLESS_API_URL}/{object_id}"
    app.logger.info(f"Attempting to DELETE user with ID {object_id} from: {user_url}")
    try:
        response = requests.delete(user_url)
        # Backendless DELETE returns 200/204 often with no content on success
        if response.status_code in (200, 204):
            return jsonify({"message": f"User {object_id} successfully deleted"}), 200

        # If the status code is something else, use the standard handler
        return backendless_response(response)

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network or API connectivity error: {e}")
        return jsonify({"error": "Failed to connect to Backendless API", "details": str(e)}), 503


if __name__ == '__main__':
    # Flask runs on port 5000 by default.
    # We use FLASK_RUN_PORT environment variable if available for deployment flexibility.
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)