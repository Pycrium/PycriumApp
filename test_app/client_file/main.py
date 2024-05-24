import socket
import threading
import pickle
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
import subprocess
import sys
import shutil

# Directory to store user data locally
LOCAL_DATA_DIR = "local_data"
if not os.path.exists(LOCAL_DATA_DIR):
    os.makedirs(LOCAL_DATA_DIR)

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
    temp_dir = os.path.join(".", "temp_game")
    os.makedirs(temp_dir, exist_ok=True)

    # Copy the entire game folder to the temporary directory
    shutil.copytree(game_dir, temp_dir, dirs_exist_ok=True)

    # Read the contents of the game folder into memory
    game_file_data = {}
    for root, _, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                game_file_data[os.path.relpath(file_path, temp_dir)] = f.read()

    # Delete the temporary directory
    shutil.rmtree(temp_dir)

    # Send the upload request to the server
    request = {
        "action": "upload",
        "username": username,
        "game_name": game_name,
        "game_file_data": game_file_data,
        "game_main_file": game_main_file,
        "game_icon": game_icon
    }
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
        self.tabs.add(self.settings_tab, text="Settings")

        self.show_games()
        self.show_create()

    def show_games(self):
        for widget in self.games_tab.winfo_children():
            widget.destroy()

        games = get_games()
        for game in games:
            game_frame = tk.Frame(self.games_tab)
            game_frame.pack(fill="x", pady=5)

            game_name = game.get("game_name")
            author = game.get("author")
            game_main_file = game.get("game_main_file")

            tk.Label(game_frame, text=f"{game_name} by {author}").pack(side="left")
            tk.Button(game_frame, text="Play", command=lambda g=game_main_file: self.play_game(g)).pack(side="right")

    def play_game(self, game_main_file):
        python_executable = sys.executable  # Get the path to the Python executable
        subprocess.run([python_executable, game_main_file])

    def show_create(self):
        for widget in self.create_tab.winfo_children():
            widget.destroy()

        tk.Button(self.create_tab, text="Upload Game", command=self.upload_game_window).pack(pady=10)

    def upload_game_window(self):
        upload_window = tk.Toplevel(self)
        upload_window.title("Upload Game")
        upload_window.geometry("400x300")

        self.game_name = tk.StringVar()
        self.game_main_file = tk.StringVar()
        self.game_icon = tk.StringVar()

        tk.Label(upload_window, text="Game Name").pack()
        tk.Entry(upload_window, textvariable=self.game_name).pack()

        tk.Label(upload_window, text="Main Game File").pack()
        self.main_file_entry = tk.Entry(upload_window, textvariable=self.game_main_file)
        self.main_file_entry.pack()
        tk.Button(upload_window, text="Select Main File", command=self.select_main_file).pack()

        tk.Label(upload_window, text="Game Icon (optional)").pack()
        tk.Entry(upload_window, textvariable=self.game_icon).pack()

        self.drop_target = tk.Label(upload_window, text="Drag and drop your game folder here", bg="lightgray")
        self.drop_target.pack(fill="both", expand=True, pady=10)
        self.drop_target.drop_target_register(DND_FILES)
        self.drop_target.dnd_bind('<<Drop>>', lambda event: self.select_game_folder(upload_window, event.data))

    def select_main_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.selected_main_file = file_path
            if hasattr(self, 'game_folder_path') and self.validate_main_file(file_path):
                self.game_main_file.set(file_path)
                self.show_upload_button()  # Call show_upload_button method

    def select_game_folder(self, upload_window, folder_path):
        if folder_path:
            username = self.local_data["username"]
            self.drop_target.config(text=f"Game folder: {folder_path}")  # Update drop target text
            self.game_folder_path = folder_path  # Store the selected game folder path
            self.upload_window = upload_window  # Store the reference to the upload window
            self.show_upload_button()  # Call show_upload_button method

    def validate_main_file(self, file_path):
        if hasattr(self, 'game_folder_path') and os.path.isfile(file_path):
            # Get the common prefix between the game folder path and the selected main file path
            common_prefix = os.path.commonprefix([self.game_folder_path, os.path.abspath(file_path)])
            # Check if the common prefix is the game folder path
            return common_prefix == os.path.abspath(self.game_folder_path) or True
        return False

    def show_upload_button(self):
        # Destroy any existing upload button
        if hasattr(self, 'upload_button'):
            self.upload_button.destroy()
        # Show the upload button if all criteria are met
        if (self.game_name.get() and self.game_main_file.get() and
                hasattr(self, 'game_folder_path')):
            self.upload_button = tk.Button(self.upload_window, text="Upload Game", command=self.upload_game)
            self.upload_button.pack(pady=10)

    def upload_game(self):
        # Retrieve the selected game name, main file, and icon
        game_name = self.game_name.get()
        game_main_file = self.game_main_file.get()
        game_icon = self.game_icon.get()

        # Check if all required fields are filled
        if not game_name or not game_main_file:
            messagebox.showerror("Incomplete Information", "Please fill in all required fields.")
            return

        # Check if the selected main file is valid
        if not self.validate_main_file(game_main_file):
            messagebox.showerror("Invalid Main File", "Please select a main file from the uploaded game folder.")
            return

        # Upload the game to the server
        username = self.local_data["username"]
        folder_path = self.game_folder_path
        if upload_game(username, game_name, folder_path, game_main_file, game_icon):
            messagebox.showinfo("Upload Success", "Game uploaded successfully")
            self.upload_window.destroy()
            self.show_create()
        else:
            messagebox.showerror("Upload Failed", "Failed to upload game")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
