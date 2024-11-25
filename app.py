from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    """
    Retrieve a list of users.
    """
    users = [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Doe"}
    ]
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Retrieve details of a specific user.
    """
    user = {"id": user_id, "name": f"User {user_id}"}
    return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.
    """
    data = request.json
    user = {
        "id": 3,
        "name": data.get("name")
    }
    return jsonify({"message": "User created", "user": user}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update details of an existing user.
    """
    data = request.json
    updated_user = {
        "id": user_id,
        "name": data.get("name"),
        "email": data.get("email")
    }
    return jsonify({"message": "User updated", "user": updated_user})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete an existing user.
    """
    return jsonify({"message": f"User {user_id} deleted"}), 204

if __name__ == '__main__':
    app.run(debug=True)
