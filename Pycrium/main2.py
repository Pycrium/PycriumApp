import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import socket
import pickle
import re

HOST = '192.168.1.3'
PORT = 1000
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.connect((HOST, PORT))

class user:
    username = ''
    password = ''
    Aurum = 0
    def check_cache():
        try:
            with open('Assets\\cache\\cache.dat', 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None, None
    def send_credentials(username, password):
        server.sendall(pickle.dumps({'function':'login_request','args':(username,password)}))
        response = pickle.loads(server.recv(1024))
        if response: user.username,user.password = username,password
        return response



class Login:

    def __init__(self,username,password):
        if username and password:
            response = user.send_credentials(username, password)
            if response:
                print("Logged in as", user.username)
            else:
                Login.login_window()
        else:
            Login.login_window()

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
                    pickle.dump((username,password),open('Assets\\cache\\cache.dat','wb+'))
                    Login(username,password)
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
            Login.login_window()

        login_button = tk.Button(root, text="Login", command=switch_to_login)
        login_button.pack()
        root.mainloop()

    def login_window():
        root = tk.Tk()
        root.title("Login")
        root.attributes('-fullscreen', True)
        root.configure(bg="black")
        
        try:
            background_image = assets.GetImage("Assets\\LoginPage\\LoginPage.jpeg")
            root.background_image = background_image  # Keep a reference to the image object
            background_label = tk.Label(root, image=background_image)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Error loading background image:", e)

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
            if user.send_credentials(username,password):
                pickle.dump((username,password),open('Assets\\cache\\cache.dat','wb+'))
                root.destroy()
            else:
                error_label['text'] = "Invalid username or password"
        login_button = tk.Button(root, text="Login", command=login)
        login_button.pack()

        def switch_to_signup():
            root.destroy()
            Login.signup_window()

        signup_button = tk.Button(root, text="Signup", command=switch_to_signup)
        signup_button.pack()
        root.mainloop()

class assets:
    def __init__(self):
        assets.LoginPage = ImageTk.PhotoImage(Image.open("Assets\\LoginPage\\LoginPage.jpeg"))
    def GetImage(address = str):
        return ImageTk.PhotoImage(Image.open(address))


username, password = user.check_cache()
Login(username,password)
server.close()
