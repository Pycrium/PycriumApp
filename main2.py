import tkinter as tk
from tkinter import ttk
import socket
import pickle

HOST = '192.168.0.110'
PORT = 1000

def check_cache():
    try:
        with open('Pycrium\\cache.dat', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None, None

def send_credentials(username, password):
    server.sendall(pickle.dumps({'function':'login_request','args':(username,password)}))
    return pickle.loads(server.recv(1024))

def signup_window():
    root = tk.Tk()
    root.title("Signup")
    username_label = tk.Label(root, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(root)
    username_entry.pack()
    password_label = tk.Label(root, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()
    confirm_password_label = tk.Label(root, text="Confirm Password:")
    confirm_password_label.pack()
    confirm_password_entry = tk.Entry(root, show="*")
    confirm_password_entry.pack()
    error_label = tk.Label(root, text="")
    error_label.pack()
    def exist_username(username):
        server.sendall(pickle.dumps({'function':'exist_username','args':username}))
        return pickle.loads(server.recv(1024)) 
    def signup():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        if exist_username(username) and password == confirm_password:
            server.sendall(pickle.dumps({'function':'add_user','args':(username,password)}))
            response = pickle.loads(server.recv(1024))
            if response:
                pickle.dump((username,password),open('Pycrium\\cache.dat','wb+'))
                root.destroy()
                print("Signed up successfully")
            else:
                error_label['text'] = "Username already exists"
        else:
            error_label['text'] = "Passwords do not match"
    signup_button = tk.Button(root, text="Signup", command=signup)
    signup_button.pack()
    def switch_to_login():
        root.destroy()
        login_window()
    login_button = tk.Button(root, text="Login", command=switch_to_login)
    login_button.pack()
    root.mainloop()

def login_window():
    root = tk.Tk()
    root.title("Login")
    username_label = tk.Label(root, text="Username:")
    username_label.pack()
    
    username_entry = tk.Entry(root)
    username_entry.pack()
    password_label = tk.Label(root, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()
    error_label = tk.Label(root, text="")
    error_label.pack()
    def login():
        username = username_entry.get()
        password = password_entry.get()
        if send_credentials(username,password):
            pickle.dump((username,password),open('Pycrium\\cache.dat','wb+'))
            root.destroy()
        else:
            error_label['text'] = "Invalid username or password"
    login_button = tk.Button(root, text="Login", command=login)
    login_button.pack()
    def switch_to_signup():
        root.destroy()
        signup_window()
    signup_button = tk.Button(root, text="Signup", command=switch_to_signup)
    signup_button.pack()
    root.mainloop()

def join(username,password):
    if username and password:
        response = send_credentials(username, password)
        if response:
            print("Logged in successfully")
        else:
            login_window()
    else:
        login_window()

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.connect((HOST, PORT))

username, password = check_cache()
join(username,password)

server.close()
