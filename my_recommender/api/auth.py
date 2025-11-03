from flask import Blueprint, jsonify, request
from ..utils.user_manager import load_users, save_users, get_next_available_user_id

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
        
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    for user in users:
        if user['username'] == username:
            return jsonify({"error": "Username already exists"}), 409
            
    new_user_id = int(get_next_available_user_id())
    new_user = {
        "id": new_user_id,
        "username": username,
        "password": password 
    }
    
    users.append(new_user)
    save_users(users)
    
    print(f"New user created: {username} (ID: {new_user_id})")
    return jsonify({
        "message": "User created successfully", 
        "userId": new_user_id,
        "username": username
    }), 201

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
        
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    for user in users:
        if user['username'] == username:
            if user['password'] == password:
                print(f"User logged in: {username} (ID: {user['id']})")
                return jsonify({
                    "message": "Login successful", 
                    "userId": user['id'],
                    "username": user['username']
                })
            else:
                return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({"error": "Invalid username or password"}), 401