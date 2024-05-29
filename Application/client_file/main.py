import socket
import threading
import pickle
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
import subprocess
import sys
import shutil
from PIL import Image, ImageTk, ImageDraw, ImageOps

# Directory to store user data locally
LOCAL_DATA_DIR = "local_data"
if not os.path.exists(LOCAL_DATA_DIR):
    os.makedirs(LOCAL_DATA_DIR)

# Directory where games are stored on the shared server
GAMES_DIR = r"D:\Aayush Paikaray\Storage"

# Server address
SERVER_ADDR = ("192.168.1.4", 9998)

# Check if user data exists locally
def load_local_data():
    try:
        with open(os.path.join(LOCAL_DATA_DIR, "user.dat"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def save_local_data(data):
    with open(os.path.join(LOCAL_DATA_DIR, "user.dat"), "wb") as f:
        pickle.dump(data, f)

# Connect to server
def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SERVER_ADDR)
    return client

# Verify credentials with server
def verify_credentials(username, password):
    client = connect_to_server()
    request = {"action": "login", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Sign up new user
def signup(username, password):
    client = connect_to_server()
    request = {"action": "signup", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Upload game to server
def upload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()

    # Copy the entire game folder to the shared directory
    dest_dir = os.path.join(GAMES_DIR, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)

    # Only send the main file path relative to the shared directory
    relative_main_file = os.path.relpath(game_main_file, GAMES_DIR)

    # Send the upload request to the server
    request = {
        "action": "upload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": game_icon
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Reupload game to server
def reupload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()

    # Copy the entire game folder to the shared directory
    dest_dir = os.path.join(GAMES_DIR, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)

    # Only send the main file path relative to the shared directory
    relative_main_file = os.path.relpath(game_main_file, GAMES_DIR)

    # Send the reupload request to the server
    request = {
        "action": "reupload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": game_icon
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Delete game from server
def delete_game(username, game_name):
    client = connect_to_server()
    request = {"action": "delete", "username": username, "game_name": game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Rename game on server
def rename_game(username, old_game_name, new_game_name):
    client = connect_to_server()
    request = {"action": "rename", "username": username, "old_game_name": old_game_name, "new_game_name": new_game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

# Retrieve list of games from server
def get_games():
    client = connect_to_server()
    request = {"action": "get_games"}
    client.send(pickle.dumps(request))
    response = client.recv(4096)
    client.close()

    if not response:
        print("No data received from server")
        return []

    try:
        games = pickle.loads(response)
        if isinstance(games, list):
            return games
        else:
            print("Invalid response format from server")
            return []
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return []

# Retrieve the currently playing count for a game from server
def get_playing_count(game_name):
    client = connect_to_server()
    request = {"action": "get_playing_count", "game_name": game_name}
    client.send(pickle.dumps(request))
    response = client.recv(4096)
    client.close()

    if not response:
        print("No data received from server")
        return 0

    try:
        playing_count = pickle.loads(response)
        if isinstance(playing_count, int):
            return playing_count
        else:
            print("Invalid response format from server")
            return 0
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return 0

# GUI Application
class Application(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client Application")
        self.geometry("600x400")
        self.local_data = load_local_data()
        if self.local_data:
            if verify_credentials(self.local_data["username"], self.local_data["password"]):
                self.show_menu()
            else:
                self.show_login()
        else:
            self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        tk.Label(self, text="Username").pack()
        tk.Entry(self, textvariable=self.username).pack()
        tk.Label(self, text="Password").pack()
        tk.Entry(self, textvariable=self.password, show="*").pack()
        tk.Button(self, text="Login", command=self.login).pack()
        tk.Button(self, text="Sign Up", command=self.show_signup).pack()

    def show_signup(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.new_username = tk.StringVar()
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()

        tk.Label(self, text="Username").pack()
        self.new_username_entry = tk.Entry(self, textvariable=self.new_username)
        self.new_username_entry.pack()
        self.new_username_entry.bind("<KeyRelease>", self.validate_username)
        self.username_error_label = tk.Label(self, text="", fg="red")
        self.username_error_label.pack()

        tk.Label(self, text="Password").pack()
        tk.Entry(self, textvariable=self.new_password, show="*").pack()
        tk.Label(self, text="Confirm Password").pack()
        tk.Entry(self, textvariable=self.confirm_password, show="*").pack()
        tk.Button(self, text="Sign Up", command=self.signup).pack()
        tk.Button(self, text="Login", command=self.show_login).pack()

    def validate_username(self, event):
        username = self.new_username.get()
        if re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
            self.username_error_label.config(text="")
        else:
            self.username_error_label.config(text="Invalid username")

    def login(self):
        username = self.username.get()
        password = self.password.get()
        if verify_credentials(username, password):
            save_local_data({"username": username, "password": password})
            self.show_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def signup(self):
        username = self.new_username.get()
        password = self.new_password.get()
        confirm_password = self.confirm_password.get()
        if password != confirm_password:
            messagebox.showerror("Signup Failed", "Passwords do not match")
            return
        if signup(username, password):
            messagebox.showinfo("Signup Success", "Account created successfully")
            self.show_login()
        else:
            messagebox.showerror("Signup Failed", "Username already exists")

    def show_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both")

        self.games_tab = ttk.Frame(self.tabs)
        self.create_tab = ttk.Frame(self.tabs)
        self.chat_tab = ttk.Frame(self.tabs)
        self.settings_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.games_tab, text="Games")
        self.tabs.add(self.create_tab, text="Create")
        self.tabs.add(self.chat_tab, text="Chat")
        self.tabs.add(self.settings_tab,text="Settings")

        self.show_games_tab()
        self.show_create_tab()
        self.show_chat_tab()
        self.show_settings_tab()

    def show_games_tab(self):
        for widget in self.games_tab.winfo_children():
            widget.destroy()

        games = get_games()
        if not games:
            tk.Label(self.games_tab, text="No games available").pack()
            return

        for game in games:
            frame = tk.Frame(self.games_tab)
            frame.pack(fill="x", pady=5)

            game_icon_path = os.path.join(GAMES_DIR, game['icon']) if game['icon'] else "default_icon.png"
            img = Image.open(game_icon_path)
            img = img.resize((64, 64), Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(img)
            tk.Label(frame, image=icon).pack(side="left", padx=5)
            frame.image = icon

            game_info = tk.Frame(frame)
            game_info.pack(side="left", fill="both", expand=True)

            tk.Label(game_info, text=game['name'], font=("Helvetica", 14, "bold")).pack(anchor="w")
            tk.Label(game_info, text=f"Uploaded by: {game['username']}").pack(anchor="w")
            tk.Label(game_info, text=f"Playing: {get_playing_count(game['name'])}").pack(anchor="w")

            btn_frame = tk.Frame(frame)
            btn_frame.pack(side="right", padx=5)

            tk.Button(btn_frame, text="Play", command=lambda g=game: self.play_game(g)).pack(side="left", padx=2)
            if game['username'] == self.local_data['username']:
                tk.Button(btn_frame, text="Reupload", command=lambda g=game: self.reupload_game(g)).pack(side="left", padx=2)
                tk.Button(btn_frame, text="Delete", command=lambda g=game: self.delete_game(g)).pack(side="left", padx=2)
                tk.Button(btn_frame, text="Rename", command=lambda g=game: self.rename_game(g)).pack(side="left", padx=2)

    def play_game(self, game):
        game_main_file = os.path.join(GAMES_DIR, game['main_file'])
        if sys.platform == "win32":
            os.startfile(game_main_file)
        else:
            subprocess.call(['open', game_main_file])

    def reupload_game(self, game):
        game_name = game['name']
        game_dir = filedialog.askdirectory(title="Select Game Directory")
        if not game_dir:
            return
        game_main_file = filedialog.askopenfilename(title="Select Main Game File", initialdir=game_dir)
        if not game_main_file:
            return
        game_icon = filedialog.askopenfilename(title="Select Game Icon", initialdir=game_dir)
        if reupload_game(self.local_data['username'], game_name, game_dir, game_main_file, game_icon):
            messagebox.showinfo("Success", "Game reuploaded successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Error", "Failed to reupload game")

    def delete_game(self, game):
        if delete_game(self.local_data['username'], game['name']):
            messagebox.showinfo("Success", "Game deleted successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Error", "Failed to delete game")

    def rename_game(self, game):
        new_name = simpledialog.askstring("Rename Game", "Enter new game name:")
        if not new_name:
            return
        if rename_game(self.local_data['username'], game['name'], new_name):
            messagebox.showinfo("Success", "Game renamed successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Error", "Failed to rename game")

    def show_create_tab(self):
        for widget in self.create_tab.winfo_children():
            widget.destroy()

        self.create_game_name = tk.StringVar()
        self.create_game_main_file = tk.StringVar()
        self.create_game_icon = tk.StringVar()

        tk.Label(self.create_tab, text="Game Name").pack()
        tk.Entry(self.create_tab, textvariable=self.create_game_name).pack()

        tk.Label(self.create_tab, text="Game Directory").pack()
        self.create_game_dir = tk.Button(self.create_tab, text="Select Directory", command=self.select_game_dir)
        self.create_game_dir.pack()

        tk.Label(self.create_tab, text="Main Game File").pack()
        self.create_game_main_file_btn = tk.Button(self.create_tab, text="Select Main File", command=self.select_main_file)
        self.create_game_main_file_btn.pack()

        tk.Label(self.create_tab, text="Game Icon").pack()
        self.create_game_icon_btn = tk.Button(self.create_tab, text="Select Icon", command=self.select_icon_file)
        self.create_game_icon_btn.pack()

        tk.Button(self.create_tab, text="Upload Game", command=self.upload_game).pack()

    def select_game_dir(self):
        self.create_game_dir = filedialog.askdirectory(title="Select Game Directory")

    def select_main_file(self):
        self.create_game_main_file.set(filedialog.askopenfilename(title="Select Main Game File", initialdir=self.create_game_dir))

    def select_icon_file(self):
        self.create_game_icon.set(filedialog.askopenfilename(title="Select Game Icon", initialdir=self.create_game_dir))

    def upload_game(self):
        game_name = self.create_game_name.get()
        game_main_file = self.create_game_main_file.get()
        game_icon = self.create_game_icon.get()

        if not game_name or not self.create_game_dir or not game_main_file:
            messagebox.showerror("Error", "Please provide all details")
            return

        if upload_game(self.local_data['username'], game_name, self.create_game_dir, game_main_file, game_icon):
            messagebox.showinfo("Success", "Game uploaded successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Error", "Failed to upload game")

    def show_chat_tab(self):
        for widget in self.chat_tab.winfo_children():
            widget.destroy()
        tk.Label(self.chat_tab, text="Chat feature not implemented yet").pack()

    def show_settings_tab(self):
        for widget in self.settings_tab.winfo_children():
            widget.destroy()
        tk.Label(self.settings_tab, text="Settings feature not implemented yet").pack()

if __name__ == "__main__":
    app = Application()
    app.mainloop()