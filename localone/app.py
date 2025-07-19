from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# @app.route('/token', methods=['GET'])
# def get_token():
#     token = os.getenv("TOKEN")
#     if not token:
#         return jsonify({"error": "Token not found"}), 404
#     return jsonify({"token": token})

# @app.route('/echo', methods=['POST'])
# def echo():
#     data = request.json
#     return jsonify(data)


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    return jsonify({"message": f"Hello, {username}!"})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    return jsonify({"message": "User created", "data": data}), 201

@app.route('/user/<username>', methods=['PUT'])
def update_user(username):
    data = request.json
    return jsonify({"message": f"User {username} updated", "data": data})

@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    return jsonify({"message": f"User {username} deleted"})

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return jsonify({"message": f"Item {item_id} details"})

if __name__ == "__main__":
    app.run(debug=True)
