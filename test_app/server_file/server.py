import socket
import threading
import pickle
import os

# Directory to store user data and games on the server
SERVER_DATA_DIR = "server_data"
USER_DATA_DIR = os.path.join(SERVER_DATA_DIR, "users")
GAME_DATA_DIR = os.path.join(SERVER_DATA_DIR, "games")
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
if not os.path.exists(GAME_DATA_DIR):
    os.makedirs(GAME_DATA_DIR)

# Server address
SERVER_ADDR = ("192.168.1.4", 9998)

# Load user data from server storage
def load_user_data(username):
    try:
        with open(os.path.join(USER_DATA_DIR, f"{username}.dat"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Save user data to server storage
def save_user_data(username, data):
    with open(os.path.join(USER_DATA_DIR, f"{username}.dat"), "wb") as f:
        pickle.dump(data, f)

# Handle game upload request
def handle_upload(client, request):
    username = request.get("username")
    game_name = request.get("game_name")
    game_file_data = request.get("game_file_data")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")

    # Create a directory for the game files
    game_dir = os.path.join(GAME_DATA_DIR, game_name)
    os.makedirs(game_dir, exist_ok=True)

    # Save the game files to the directory
    for file_name, file_data in game_file_data.items():
        file_path = os.path.join(game_dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_data)

    # Save the main file and icon file paths to a metadata file
    metadata = {
        "main_file": game_main_file,
        "icon_file": game_icon
    }
    with open(os.path.join(game_dir, "metadata.dat"), "wb") as f:
        pickle.dump(metadata, f)

    response = {"status": "success"}
    client.send(pickle.dumps(response))

# Retrieve list of games from server
def get_games():
    games = []
    for game_name in os.listdir(GAME_DATA_DIR):
        game_dir = os.path.join(GAME_DATA_DIR, game_name)
        if os.path.isdir(game_dir):
            metadata_file = os.path.join(game_dir, "metadata.dat")
            if os.path.exists(metadata_file):
                with open(metadata_file, "rb") as f:
                    metadata = pickle.load(f)
                    games.append({
                        "game_name": game_name,
                        "main_file": metadata["main_file"],
                        "icon_file": metadata["icon_file"]
                    })
    return games

# Handle client requests
def handle_client(client, addr):
    print(f"Connection from {addr}")
    try:
        request = pickle.loads(client.recv(4096))
        action = request.get("action")

        if action == "login":
            username = request.get("username")
            password = request.get("password")
            user_data = load_user_data(username)
            if user_data and user_data.get("password") == password:
                response = {"status": "success"}
            else:
                response = {"status": "fail"}
            client.send(pickle.dumps(response))

        elif action == "signup":
            username = request.get("username")
            password = request.get("password")
            if load_user_data(username):
                response = {"status": "fail"}
            else:
                save_user_data(username, {"username": username, "password": password})
                response = {"status": "success"}
            client.send(pickle.dumps(response))

        elif action == "upload":
            handle_upload(client, request)

        elif action == "get_games":
            games = get_games()
            client.send(pickle.dumps(games))

        # Add other actions as needed

    except Exception as e:
        print(f"Error: {e}")
        response = {"status": "error", "message": str(e)}
        client.send(pickle.dumps(response))
    finally:
        client.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SERVER_ADDR)
    server.listen(5)
    print(f"Server started on {SERVER_ADDR}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    start_server()
