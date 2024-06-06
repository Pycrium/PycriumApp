import socket
import pickle
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
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

# Directory to store game icons
ICONS_DIR = os.path.join(GAMES_DIR, "Icons")
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR)

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

# Copy the icon to the storage/icons directory
def copy_icon_to_storage(icon_path):
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon file not found: {icon_path}")
    
    icon_name = os.path.basename(icon_path)
    dest_icon_path = os.path.join(ICONS_DIR, icon_name)
    shutil.copyfile(icon_path, dest_icon_path)
    return dest_icon_path

# Upload game to server
def upload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()

    # Copy the entire game folder to the shared directory
    dest_dir = os.path.join(GAMES_DIR, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)

    # Only send the main file path relative to the shared directory
    relative_main_file = os.path.relpath(game_main_file, GAMES_DIR)

    # Copy the icon to the storage/icons directory
    dest_icon_path = copy_icon_to_storage(game_icon)

    # Send the upload request to the server
    request = {
        "action": "upload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": os.path.relpath(dest_icon_path, GAMES_DIR)
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

    # Copy the icon to the storage/icons directory
    dest_icon_path = copy_icon_to_storage(game_icon)

    # Send the reupload request to the server
    request = {
        "action": "reupload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": os.path.relpath(dest_icon_path, GAMES_DIR)
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
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client Application")
        self.configure(bg="#2b2b2b")  # Set background color to dark gray
        self.attributes("-fullscreen", True)  # Maximize window
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

        tk.Label(self, text="Username", bg="#2b2b2b", fg="white").pack()
        tk.Entry(self, textvariable=self.username, bg="#444444", fg="white").pack()
        tk.Label(self, text="Password", bg="#2b2b2b", fg="white").pack()
        tk.Entry(self, textvariable=self.password, show="*", bg="#444444", fg="white").pack()
        tk.Button(self, text="Login", command=self.login, bg="#444444", fg="white").pack()
        tk.Button(self, text="Sign Up", command=self.show_signup, bg="#444444", fg="white").pack()

    def show_signup(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.new_username = tk.StringVar()
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()

        tk.Label(self, text="Username", bg="#2b2b2b", fg="white").pack()
        self.new_username_entry = tk.Entry(self, textvariable=self.new_username, bg="#444444", fg="white")
        self.new_username_entry.pack()
        self.new_username_entry.bind("<KeyRelease>", self.validate_username)
        self.username_error_label = tk.Label(self, text="", fg="red", bg="#2b2b2b")
        self.username_error_label.pack()

        tk.Label(self, text="Password", bg="#2b2b2b", fg="white").pack()
        tk.Entry(self, textvariable=self.new_password, show="*", bg="#444444", fg="white").pack()
        tk.Label(self, text="Confirm Password", bg="#2b2b2b", fg="white").pack()
        tk.Entry(self, textvariable=self.confirm_password, show="*", bg="#444444", fg="white").pack()
        tk.Button(self, text="Sign Up", command=self.signup, bg="#444444", fg="white").pack()
        tk.Button(self, text="Login", command=self.show_login, bg="#444444", fg="white").pack()

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
        num_games = len(games)
        max_columns = 7  # Maximum number of games per row
        num_columns = min(max_columns, max(1, int(self.winfo_width() / 200)))  # Adjust based on window width
        num_rows = (num_games + num_columns - 1) // num_columns

        canvas = tk.Canvas(self.games_tab)
        scrollbar = tk.Scrollbar(self.games_tab, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas, bg="#2b2b2b")  # Set background color to dark gray
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

        for i, game in enumerate(games):
            game_frame = tk.Frame(frame, bd=2, relief="groove", bg="#444444", width=200, height=280)  # Set background color to dark gray
            game_frame.pack_propagate(False)  # Prevent frame from shrinking to fit its content

            game_name = game.get("game_name")
            author = game.get("username")
            game_main_file = game.get("main_file")
            playing_count = get_playing_count(game_name)

            icon_path = os.path.join(GAMES_DIR, game.get("icon", ""))
            if icon_path and os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize((180, 180))  # Adjust thumbnail size
                    thumbnail = ImageTk.PhotoImage(img)
                    thumbnail_label = tk.Label(game_frame, image=thumbnail, bd=0)
                    thumbnail_label.image = thumbnail
                    thumbnail_label.pack(pady=(5, 10))
                except Exception as e:
                    print(f"Error loading image {icon_path}: {e}")
            else:
                print("Icon file not found")  # Debug print

            # Wrap text within a certain width
            name_label = tk.Label(game_frame, text=game_name, font=("Helvetica", 12, "bold"), wraplength=180, bg="#444444", fg="white")
            name_label.pack()

            author_label = tk.Label(game_frame, text=f"by {author}", font=("Helvetica", 10), bg="#444444", fg="white")
            author_label.pack()

            count_label = tk.Label(game_frame, text=f"Players: {playing_count}", font=("Helvetica", 10), bg="#444444", fg="white")
            count_label.pack()

            thumbnail_label.bind("<Button-1>", lambda event, game_main_file=game_main_file: self.play_game(game_main_file))

            row_num = i // num_columns
            col_num = i % num_columns
            game_frame.grid(row=row_num, column=col_num, padx=10, pady=10, sticky="nsew")

        for i in range(num_rows):
            frame.grid_rowconfigure(i, weight=1)  # Allow rows to expand
        for j in range(num_columns):
            frame.grid_columnconfigure(j, weight=1)  # Allow columns to expand

        # Enable mouse wheel scrolling
        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        self.games_tab.update_idletasks()  # Update the tab to ensure proper rendering



    def play_game(self, game_main_file):
        game_main_file_path = os.path.join(GAMES_DIR, game_main_file)
        game_dir = os.path.dirname(game_main_file_path) 

        self.update_playing_count(game_main_file, 1)
        os.chdir(game_dir)
        python_executable = sys.executable 
        subprocess.Popen([python_executable, game_main_file_path])

        self.after(5000, self.update_playing_count, game_main_file, -1)

    def update_playing_count(self, game_name, count_change):
        client = connect_to_server()
        request = {"action": "update_playing_count", "game_name": game_name, "count_change": count_change}
        client.send(pickle.dumps(request))
        client.close()

    def show_create(self):
        for widget in self.create_tab.winfo_children():
            widget.destroy()

        tk.Button(self.create_tab, text="Upload Game", command=self.upload_game_window, bg="#444444", fg="white").pack(pady=10)

        games = get_games()
        for game in games:
            if game.get("username") == self.local_data["username"]:
                game_frame = tk.Frame(self.create_tab)
                game_frame.pack(fill="x", pady=5)

                game_name = game.get("game_name")

                tk.Label(game_frame, text=game_name, bg="#2b2b2b", fg="white").pack(side="left")
                tk.Button(game_frame, text="Reupload", command=lambda g=game_name: self.reupload_game_window(g), bg="#444444", fg="white").pack(side="left")
                tk.Button(game_frame, text="Delete", command=lambda g=game_name: self.delete_game(g), bg="#444444", fg="white").pack(side="left")
                tk.Button(game_frame, text="Rename", command=lambda g=game_name: self.rename_game_window(g), bg="#444444", fg="white").pack(side="left")

    def reupload_game_window(self, game_name):
        game_dir = filedialog.askdirectory(title="Select Game Directory")
        if game_dir:
            game_main_file = filedialog.askopenfilename(title="Select Main Game File", initialdir=game_dir)
            game_icon = filedialog.askopenfilename(title="Select Game Icon", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if game_main_file and game_icon:
                if reupload_game(self.local_data["username"], game_name, game_dir, game_main_file, game_icon):
                    messagebox.showinfo("Success", "Game reuploaded successfully")
                    self.show_create()
                else:
                    messagebox.showerror("Error", "Failed to reupload game")

    def delete_game(self, game_name):
        if delete_game(self.local_data["username"], game_name):
            messagebox.showinfo("Success", "Game deleted successfully")
            self.show_create()
        else:
            messagebox.showerror("Error", "Failed to delete game")

    def rename_game_window(self, game_name):
        new_name = simpledialog.askstring("Rename Game", "Enter new game name:")
        if new_name:
            if rename_game(self.local_data["username"], game_name, new_name):
                messagebox.showinfo("Success", "Game renamed successfully")
                self.show_create()
            else:
                messagebox.showerror("Error", "Failed to rename game")

    def upload_game_window(self):
        game_name = simpledialog.askstring("Game Name", "Enter game name:")
        game_dir = filedialog.askdirectory(title="Select Game Directory")
        if game_dir:
            game_main_file = filedialog.askopenfilename(title="Select Main Game File", initialdir=game_dir)
            game_icon = filedialog.askopenfilename(title="Select Game Icon", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if game_name and game_main_file and game_icon:
                if upload_game(self.local_data["username"], game_name, game_dir, game_main_file, game_icon):
                    messagebox.showinfo("Success", "Game uploaded successfully")
                    self.show_create()
                else:
                    messagebox.showerror("Error", "Failed to upload game")

# Run the application
if __name__ == "__main__":
    app = Application()
    app.mainloop()

