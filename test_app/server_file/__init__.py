import socket
import threading
import pickle
import os
import hashlib

# Directory to store user data
USERS_DIR = "users_data"
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# Directory where games are stored on the shared server
GAMES_DIR = "path_to_shared_storage_directory"
if not os.path.exists(GAMES_DIR):
    os.makedirs(GAMES_DIR)

# Load user data
def load_user_data():
    users = {}
    for filename in os.listdir(USERS_DIR):
        filepath = os.path.join(USERS_DIR, filename)
        with open(filepath, "rb") as f:
            user_data = pickle.load(f)
            users[user_data["username"]] = user_data
    return users

def save_user_data(user_data):
    filepath = os.path.join(USERS_DIR, f"{user_data['username']}.dat")
    with open(filepath, "wb") as f:
        pickle.dump(user_data, f)

users = load_user_data()

# Handle client connections
def handle_client(client_socket):
    request = pickle.loads(client_socket.recv(4096))
    action = request.get("action")

    if action == "signup":
        handle_signup(client_socket, request)
    elif action == "login":
        handle_login(client_socket, request)
    elif action == "upload":
        handle_upload(client_socket, request)
    elif action == "get_games":
        handle_get_games(client_socket)
    else:
        client_socket.send(pickle.dumps({"status": "error", "message": "Unknown action"}))
    client_socket.close()

def handle_signup(client_socket, request):
    username = request.get("username")
    password = request.get("password")

    if username in users:
        client_socket.send(pickle.dumps({"status": "error", "message": "Username already exists"}))
    else:
        user_data = {"username": username, "password": hashlib.sha256(password.encode()).hexdigest(), "games": []}
        users[username] = user_data
        save_user_data(user_data)
        client_socket.send(pickle.dumps({"status": "success"}))

def handle_login(client_socket, request):
    username = request.get("username")
    password = request.get("password")

    user_data = users.get(username)
    if user_data and user_data["password"] == hashlib.sha256(password.encode()).hexdigest():
        client_socket.send(pickle.dumps({"status": "success"}))
    else:
        client_socket.send(pickle.dumps({"status": "error", "message": "Invalid credentials"}))

def handle_upload(client_socket, request):
    username = request.get("username")
    game_name = request.get("game_name")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")

    user_data = users.get(username)
    if user_data:
        game_data = {
            "game_name": game_name,
            "main_file": game_main_file,
            "icon": game_icon
        }
        user_data["games"].append(game_data)
        save_user_data(user_data)
        client_socket.send(pickle.dumps({"status": "success"}))
    else:
        client_socket.send(pickle.dumps({"status": "error", "message": "User not found"}))

def handle_get_games(client_socket):
    all_games = []
    for user_data in users.values():
        for game in user_data.get("games", []):
            all_games.append({"username": user_data["username"], "game_name": game["game_name"], "main_file": game["main_file"], "icon": game["icon"]})
    client_socket.send(pickle.dumps(all_games))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9998))
    server.listen(5)
    print("Server started on port 9998")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()