import socket
import threading
import pickle
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
import subprocess
import sys
import shutil
from PIL import Image, ImageTk

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
        self.tabs.add(self.settings_tab, text('-fullscreen', True)
        root.configure(bg="black")

        def on_entry_click(event, text, entry_object):
            if entry_object.get() == text:
                entry_object.delete(0, "end")
                entry_object['fg'] = '#FFFFFF'
                if entry_object in [password_entry]:
                    entry_object.config(show="*")

        def on_focus_out(event, text, entry_object):
            if entry_object.get() == '':
                entry_object['fg'] = '#CCCCCC'
                entry_object.insert(0, text)
                entry_object.config(show="")

        def validate_username(username):
            if not re.match(r'^[a-zA-Z0-9]{3,20}$', username):
                username_error_label['text'] = "Username must be 3-20 alphanumeric characters only"
                return False
            if not exist_username(username):
                username_error_label['text'] = "Username does not exist"
                return False
            username_error_label['text'] = ""
            return True

        def validate_password(password):
            password_error_label['text'] = ""
            return True

        def exist_username(username):
            server.sendall(pickle.dumps({'function': 'exist_username', 'args': username}))
            return pickle.loads(server.recv(1024))

        try:
            background_image = assets.GetImage("Assets\\LoginPage\\LoginPage.jpeg")
            root.background_image = background_image
            background_label = tk.Label(root, image=background_image, bg='Black')
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Error loading background image:", e)

        username_entry = tk.Entry(root, font=('Gill Sans Ultra Bold', 20), fg='#CCCCCC', bg="#2D3E45", width=21, borderwidth=0, highlightthickness=0)
        username_entry.bind('<FocusIn>', lambda event: on_entry_click(event, "Username", username_entry))
        username_entry.bind('<FocusOut>', lambda event: on_focus_out(event, "Username", username_entry))
        username_entry.bind('<KeyRelease>', lambda event: validate_username(username_entry.get()))
        username_entry.insert(0, 'Username')
        username_entry.bind('<KeyPress>', lambda event: "break" if event.char == " " else None)
        username_entry.config(insertofftime=1000000)
        username_entry.place(x=415, y=480)

        password_entry = tk.Entry(root, font=('Gill Sans Ultra Bold', 20), fg='#CCCCCC', bg="#2D3E45", width=21, borderwidth=0, highlightthickness=0)
        password_entry.insert(0, 'Password')
        password_entry.config(insertofftime=1000000)
        password_entry.bind('<FocusIn>', lambda event: on_entry_click(event, "Password", password_entry))
        password_entry.bind('<FocusOut>', lambda event: on_focus_out(event, "Password", password_entry))
        password_entry.bind('<KeyRelease>', lambda event: validate_password(password_entry.get()))
        password_entry.bind('<KeyPress>', lambda event: "break" if event.char == " " else None)
        password_entry.place(x=415, y=551)

        username_error_label = tk.Label(root, text='', font=('Helvetica', 10), fg='#CCCCCC', bg="#2D3E45", borderwidth=0, highlightthickness=0, anchor='e', width=38)
        username_error_label.place(x=650, y=471)

        password_error_label = tk.Label(root, text='', font=('Helvetica', 10), fg='#CCCCCC', bg="#2D3E45", borderwidth=0, highlightthickness=0, anchor='e', width=40)
        password_error_label.place(x=640, y=548)

        def login():
            username = username_entry.get()
            password = password_entry.get()

            server.sendall(pickle.dumps({'function': 'login_request', 'args': (username, password)}))
            response = pickle.loads(server.recv(1024))
            if response:
                pickle.dump((username, password), open('Assets\\cache\\cache.dat', 'wb+'))
                root.destroy()
                print("Logged in successfully")
            else:
                username_error_label['text'] = "Invalid username or password."

        login_button = tk.Button(root, text="Login", command=login, font=('Gill Sans Ultra Bold', 25), fg='white', bg="#2D3E45", width=16, borderwidth=0, highlightthickness=0, activebackground="#2D3E45", activeforeground='black')
        login_button.place(x=499, y=683)
        password_entry.bind('<Return>', lambda event: login())

        def switch_to_signup():
            root.destroy()
            Login.signup_window()

        signup_button = tk.Button(root, text="Don't have an account? Signup", command=switch_to_signup, bg='#303040', fg='white', borderwidth=0, relief="flat", activeforeground='#4099FF', activebackground='#303040')
        signup_button.place(x=1145, y=745)

        root.mainloop()


if __name__ == "__main__":
    # Try to load cached credentials
    cached_username, cached_password = user.check_cache()
    if cached_username and cached_password:
        Login(cached_username, cached_password)
    else:
        Login.login_window()