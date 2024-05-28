import socket
import threading
import pickle
import os
import shutil

# Directory where games are stored
GAMES_DIR = r"D:\Aayush Paikaray\Storage"

# Server address
SERVER_ADDR = ("0.0.0.0", 9998)

# In-memory store to keep track of currently playing counts
currently_playing_counts = {}

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDR)
server.listen(5)
print("Server started...")

# Load user data
def load_user_data():
    if os.path.exists("users.dat"):
        with open("users.dat", "rb") as f:
            return pickle.load(f)
    return {}

# Save user data
def save_user_data(data):
    with open("users.dat", "wb") as f:
        pickle.dump(data, f)

# Load games data
def load_games_data():
    if os.path.exists("games.dat"):
        with open("games.dat", "rb") as f:
            return pickle.load(f)
    return []

# Save games data
def save_games_data(data):
    with open("games.dat", "wb") as f:
        pickle.dump(data, f)

# Handle client connection
def handle_client(conn):
    try:
        request = pickle.loads(conn.recv(4096))
        action = request.get("action")

        if action == "login":
            handle_login(conn, request)
        elif action == "signup":
            handle_signup(conn, request)
        elif action == "upload":
            handle_upload(conn, request)
        elif action == "reupload":
            handle_reupload(conn, request)
        elif action == "delete":
            handle_delete(conn, request)
        elif action == "rename":
            handle_rename(conn, request)
        elif action == "get_games":
            handle_get_games(conn)
        elif action == "get_playing_count":
            handle_get_playing_count(conn, request)
        elif action == "update_playing_count":
            handle_update_playing_count(conn, request)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

# Handle login
def handle_login(conn, request):
    username = request.get("username")
    password = request.get("password")
    users = load_user_data()
    if users.get(username) == password:
        response = {"status": "success"}
    else:
        response = {"status": "failure"}
    conn.send(pickle.dumps(response))

# Handle signup
def handle_signup(conn, request):
    username = request.get("username")
    password = request.get("password")
    users = load_user_data()
    if username in users:
        response = {"status": "failure"}
    else:
        users[username] = password
        save_user_data(users)
        response = {"status": "success"}
    conn.send(pickle.dumps(response))

# Handle upload
def handle_upload(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")

    games = load_games_data()
    games.append({
        "game_name": game_name,
        "username": username,
        "main_file": game_main_file,
        "icon": game_icon
    })
    save_games_data(games)
    response = {"status": "success"}
    conn.send(pickle.dumps(response))

# Handle reupload
def handle_reupload(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")

    games = load_games_data()
    for game in games:
        if game["game_name"] == game_name and game["username"] == username:
            game["main_file"] = game_main_file
            game["icon"] = game_icon
            save_games_data(games)
            response = {"status": "success"}
            conn.send(pickle.dumps(response))
            return
    response = {"status": "failure"}
    conn.send(pickle.dumps(response))

# Handle delete
def handle_delete(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")

    games = load_games_data()
    games = [game for game in games if not (game["game_name"] == game_name and game["username"] == username)]
    save_games_data(games)

    game_dir = os.path.join(GAMES_DIR, game_name)
    if os.path.exists(game_dir):
        shutil.rmtree(game_dir)

    response = {"status": "success"}
    conn.send(pickle.dumps(response))

# Handle rename
def handle_rename(conn, request):
    old_game_name = request.get("old_game_name")
    new_game_name = request.get("new_game_name")
    username = request.get("username")

    games = load_games_data()
    for game in games:
        if game["game_name"] == old_game_name and game["username"] == username:
            game["game_name"] = new_game_name
            save_games_data(games)

            old_game_dir = os.path.join(GAMES_DIR, old_game_name)
            new_game_dir = os.path.join(GAMES_DIR, new_game_name)
            if os.path.exists(old_game_dir):
                os.rename(old_game_dir, new_game_dir)

            response = {"status": "success"}
            conn.send(pickle.dumps(response))
            return
    response = {"status": "failure"}
    conn.send(pickle.dumps(response))

# Handle get games
def handle_get_games(conn):
    games = load_games_data()
    conn.send(pickle.dumps(games))

# Handle get playing count
def handle_get_playing_count(conn, request):
    game_name = request.get("game_name")
    count = currently_playing_counts.get(game_name, 0)
    conn.send(pickle.dumps(count))
# Handle update playing count
def handle_update_playing_count(conn, request):
    game_name = request.get("game_name")
    count_change = request.get("count_change", 0)
    if game_name in currently_playing_counts:
        currently_playing_counts[game_name] += count_change
    else:
        currently_playing_counts[game_name] = count_change
    conn.send(pickle.dumps({"status": "success"}))



# Main server loop
def main():
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    main()
