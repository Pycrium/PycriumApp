import socket
import threading
import pickle
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import re
import subprocess
import sys
import shutil
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

# Directory to store user data locally
LOCAL_DATA_DIR = "local_data"
if not os.path.exists(LOCAL_DATA_DIR):
    os.makedirs(LOCAL_DATA_DIR)

# Directory where games are stored on the shared server
GAMES_DIR = r"D:\Aayush Paikaray\Storage"

# Server address
SERVER_ADDR = ("192.168.1.4", 9998)

def load_local_data():
    try:
        with open(os.path.join(LOCAL_DATA_DIR, "user.dat"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def save_local_data(data):
    with open(os.path.join(LOCAL_DATA_DIR, "user.dat"), "wb") as f:
        pickle.dump(data, f)

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SERVER_ADDR)
    return client

def verify_credentials(username, password):
    client = connect_to_server()
    request = {"action": "login", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def signup(username, password):
    client = connect_to_server()
    request = {"action": "signup", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def upload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()

    dest_dir = os.path.join(GAMES_DIR, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)

    relative_main_file = os.path.relpath(game_main_file, GAMES_DIR)

    if game_icon.startswith(game_dir):
        relative_icon = os.path.relpath(game_icon, game_dir)
    else:
        icon_name = os.path.basename(game_icon)
        dest_icon_path = os.path.join(GAMES_DIR, icon_name)
        shutil.copy2(game_icon, dest_icon_path)
        relative_icon = icon_name

    request = {
        "action": "upload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": relative_icon
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def reupload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()

    dest_dir = os.path.join(GAMES_DIR, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)

    relative_main_file = os.path.relpath(game_main_file, GAMES_DIR)

    if game_icon.startswith(game_dir):
        relative_icon = os.path.relpath(game_icon, game_dir)
    else:
        icon_name = os.path.basename(game_icon)
        dest_icon_path = os.path.join(GAMES_DIR, icon_name)
        shutil.copy2(game_icon, dest_icon_path)
        relative_icon = icon_name

    request = {
        "action": "reupload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": relative_icon
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def delete_game(username, game_name):
    client = connect_to_server()
    request = {"action": "delete", "username": username, "game_name": game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def rename_game(username, old_game_name, new_game_name):
    client = connect_to_server()
    request = {"action": "rename", "username": username, "old_game_name": old_game_name, "new_game_name": new_game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

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

class Application(ThemedTk):
    def __init__(self):
        super().__init__(theme="equilux")
        self.title("Client Application")
        self.state("zoomed")  # Maximize window
        self.local_data = load_local_data()

        # Apply custom styles
        style = ttk.Style(self)
        style.configure("TLabel", foreground="white", background="#333333", font=("Arial", 14))
        style.configure("TButton", foreground="white", background="#444444", font=("Arial", 12))
        style.map("TButton", background=[('active', '#555555')])
        style.configure("TFrame", background="#333333")
        style.configure("TEntry", fieldbackground="#555555", foreground="white", font=("Arial", 12))
        style.configure("TNotebook", background="#333333", tabmargins=2)
        style.configure("TNotebook.Tab", background="#444444", foreground="white")
        style.map("TNotebook.Tab", background=[('selected', '#555555')])

        self.configure(bg="#333333")

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

        tk.Label(self, text="Username", bg="#333333", fg="white").pack(pady=10)
        tk.Entry(self, textvariable=self.username, bg="#555555", fg="white").pack()
        tk.Label(self, text="Password", bg="#333333", fg="white").pack(pady=10)
        tk.Entry(self, textvariable=self.password, show="*", bg="#555555", fg="white").pack()
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Sign Up", command=self.show_signup).pack()

    def show_signup(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.new_username = tk.StringVar()
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()

        tk.Label(self, text="Username", bg="#333333", fg="white").pack(pady=10)
        tk.Entry(self, textvariable=self.new_username, bg="#555555", fg="white").pack()
        tk.Label(self, text="Password", bg="#333333", fg="white").pack(pady=10)
        tk.Entry(self, textvariable=self.new_password, show="*", bg="#555555", fg="white").pack()
        tk.Label(self, text="Confirm Password", bg="#333333", fg="white").pack(pady=10)
        tk.Entry(self, textvariable=self.confirm_password, show="*", bg="#555555", fg="white").pack()
        ttk.Button(self, text="Sign Up", command=self.signup).pack(pady=10)
        ttk.Button(self, text="Login", command=self.show_login).pack()

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

        self.show_games_tab()
        self.show_create_tab()
        self.show_chat_tab()
        self.show_settings_tab()

    def show_games_tab(self):
        for widget in self.games_tab.winfo_children():
            widget.destroy()

        games = get_games()
        if not games:
            tk.Label(self.games_tab, text="No games available", bg="#333333", fg="white", font=("Arial", 14)).pack()
            return

        for game in games:
            frame = ttk.Frame(self.games_tab)
            frame.pack(fill="x", pady=5)

            game_icon_path = os.path.join(GAMES_DIR, game['icon']) if game['icon'] else "default_icon.png"
            img = Image.open(game_icon_path)
            img = img.resize((64, 64), Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(img)
            tk.Label(frame, image=icon, bg="#333333").pack(side="left", padx=5)
            frame.image = icon

            game_info = ttk.Frame(frame)
            game_info.pack(side="left", fill="both", expand=True)

            ttk.Label(game_info, text=game['name'], font=("Helvetica", 14, "bold"), background="#333333", foreground="white").pack(anchor="w")
            ttk.Label(game_info, text=f"Uploaded by: {game['username']}", background="#333333", foreground="white").pack(anchor="w")
            ttk.Label(game_info, text=f"Playing: {get_playing_count(game['name'])}", background="#333333", foreground="white").pack(anchor="w")

            btn_frame = ttk.Frame(frame)
            btn_frame.pack(side="right", padx=5)

            ttk.Button(btn_frame, text="Play", command=lambda g=game: self.play_game(g)).pack(side="left", padx=2)
            if game['username'] == self.local_data['username']:
                ttk.Button(btn_frame, text="Reupload", command=lambda g=game: self.reupload_game(g)).pack(side="left", padx=2)
                ttk.Button(btn_frame, text="Delete", command=lambda g=game: self.delete_game(g)).pack(side="left", padx=2)
                ttk.Button(btn_frame, text="Rename", command=lambda g=game: self.rename_game(g)).pack(side="left", padx=2)

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
            messagebox.showinfo("Reupload Successful", "Game reuploaded successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Reupload Failed", "Failed to reupload game")

    def delete_game(self, game):
        game_name = game['name']
        confirmation = messagebox.askyesno("Delete Game", f"Are you sure you want to delete {game_name}?")
        if confirmation:
            if delete_game(self.local_data['username'], game_name):
                messagebox.showinfo("Delete Successful", "Game deleted successfully")
                self.show_games_tab()
            else:
                messagebox.showerror("Delete Failed", "Failed to delete game")

    def rename_game(self, game):
        old_game_name = game['name']
        new_game_name = simpledialog.askstring("Rename Game", f"New name for {old_game_name}:")
        if new_game_name:
            if rename_game(self.local_data['username'], old_game_name, new_game_name):
                messagebox.showinfo("Rename Successful", "Game renamed successfully")
                self.show_games_tab()
            else:
                messagebox.showerror("Rename Failed", "Failed to rename game")

    def show_create_tab(self):
        for widget in self.create_tab.winfo_children():
            widget.destroy()

        tk.Label(self.create_tab, text="Create New Game", bg="#333333", fg="white", font=("Arial", 16, "bold")).pack(pady=10)

        self.game_name_entry = ttk.Entry(self.create_tab)
        self.game_name_entry.pack(pady=5)

        ttk.Button(self.create_tab, text="Select Directory", command=self.select_game_directory).pack(pady=5)
        ttk.Button(self.create_tab, text="Select Main File", command=self.select_main_file).pack(pady=5)
        ttk.Button(self.create_tab, text="Select Icon", command=self.select_game_icon).pack(pady=5)
        ttk.Button(self.create_tab, text="Upload Game", command=self.upload_new_game).pack(pady=10)

    def select_game_directory(self):
        game_dir = filedialog.askdirectory(title="Select Game Directory")
        if game_dir:
            self.game_dir = game_dir

    def select_main_file(self):
        game_main_file = filedialog.askopenfilename(title="Select Main Game File", initialdir=self.game_dir)
        if game_main_file:
            self.game_main_file = game_main_file

    def select_game_icon(self):
        game_icon = filedialog.askopenfilename(title="Select Game Icon", initialdir=self.game_dir)
        if game_icon:
            self.game_icon = game_icon

    def upload_new_game(self):
        game_name = self.game_name_entry.get().strip()
        if not game_name:
            messagebox.showerror("Error", "Please enter a name for the game")
            return
        if not hasattr(self, 'game_dir') or not hasattr(self, 'game_main_file') or not hasattr(self, 'game_icon'):
            messagebox.showerror("Error", "Please select game directory, main file, and icon")
            return
        if upload_game(self.local_data['username'], game_name, self.game_dir, self.game_main_file, self.game_icon):
            messagebox.showinfo("Upload Successful", "Game uploaded successfully")
            self.show_games_tab()
        else:
            messagebox.showerror("Upload Failed", "Failed to upload game")

    def show_chat_tab(self):
        for widget in self.chat_tab.winfo_children():
            widget.destroy()

        tk.Label(self.chat_tab, text="Chat", bg="#333333", fg="white", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Text(self.chat_tab, bg="#555555", fg="white", height=10, width=50).pack(pady=5)

    def show_settings_tab(self):
        for widget in self.settings_tab.winfo_children():
            widget.destroy()

        tk.Label(self.settings_tab, text="Settings", bg="#333333", fg="white", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Button(self.settings_tab, text="Logout", command=self.logout).pack(pady=10)

    def logout(self):
        os.remove(os.path.join(LOCAL_DATA_DIR, "user.dat"))
        self.destroy()
        Application()

if __name__ == "__main__":
    app = Application()
    app.mainloop()