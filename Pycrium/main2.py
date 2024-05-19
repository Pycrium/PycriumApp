import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import socket
import pickle
import re

HOST = '192.168.1.4'
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

        def on_entry_click(event,text,object):
            if object.get()==text:
                object.delete(0,"end")  
                if object==password_entry:object.config(show="*")  

        def on_focus_out(event,text,object):
            if object.get()=='':
                object.insert(0,text)
                object.config(show="")

        try:
            background_image = assets.GetImage("Assets\\LoginPage\\LoginPage.jpeg")
            root.background_image = background_image
            background_label = tk.Label(root, image=background_image, bg='Black')
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Error loading background image:", e)

        username_entry = tk.Entry(root,font=('Gill Sans Ultra Bold',23),fg='White',bg="#2D3E45", width=21,borderwidth=0,highlightthickness=0)
        username_entry.bind('<FocusIn>', lambda event:on_entry_click(event,"Username",username_entry))
        username_entry.bind('<FocusOut>', lambda event:on_focus_out(event,"Username",username_entry))
        username_entry.insert(0, 'Username')
        username_entry.bind('<KeyPress>', lambda event:"break" if event.char == " " else None)
        username_entry.config(insertofftime=1000000)
        username_entry.place(x=416,y=478)

        password_entry = tk.Entry(root, font=('Gill Sans Ultra Bold', 23), fg='white', bg="#2D3E45", width=21, borderwidth=0, highlightthickness=0)
        password_entry.insert(0, 'Password')
        password_entry.config(insertofftime=1000000)
        password_entry.bind('<FocusIn>', lambda event:on_entry_click(event,"Password",password_entry))
        password_entry.bind('<FocusOut>', lambda event:on_focus_out(event,"Password",password_entry))
        password_entry.bind('<KeyPress>', lambda event:"break" if event.char == " " else None)
        password_entry.place(x=415, y=553)
    
        # def right_click(event):
        #     print(event.x,event.y)
        # background_label.bind('<Motion>',right_click)

        def login():
            username = username_entry.get()
            password = password_entry.get()
            if user.send_credentials(username,password):
                pickle.dump((username,password),open('Assets\\cache\\cache.dat','wb+'))
                root.destroy()
            else:
                login_button['fg']='Red'
                login_button['text']='Invalid Credentials'
                root.after(2000,error_box)
        login_button = tk.Button(root,text="Login     ",command=login,font=('Gill Sans Ultra Bold',25),fg='white',bg="#2D3E45",width=14,borderwidth=0,highlightthickness=0,activebackground="#2D3E45",activeforeground='black')
        login_button.place(x=517,y=683)
        password_entry.bind('<Return>',lambda event:login())

        def error_box():
            login_button['text']="Login     ";login_button['fg']='White'
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
