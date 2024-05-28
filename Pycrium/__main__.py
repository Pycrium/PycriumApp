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
        root.attributes('-fullscreen', True)
        root.configure(bg="black")

        def on_entry_click(event, text, entry_object):
            if entry_object.get() == text:
                entry_object.delete(0, "end")
                entry_object['fg'] = '#FFFFFF'
                if entry_object in [password_entry, confirm_password_entry]:
                    entry_object.config(show="*")

        def on_focus_out(event, text, entry_object):
            if entry_object.get() == '':
                entry_object['fg'] = '#CCCCCC'
                entry_object.insert(0, text)
                entry_object.config(show="")

        def validate_username(username):
            if not re.match(r'^[a-zA-Z0-9]{3,20}$', username):
                username_error_label['text'] = "username must be 3-20 alphanumeric charaters only"
                return False
            if not exist_username(username):
                username_error_label['text'] = "username already exists"
                return False
            username_error_label['text'] = ""
            return True

        def validate_password(password):
            if len(password) < 8:
                password_error_label['text'] = "Password must be at least 8 characters."
                return False
            if not re.search(r'[A-Z]', password):
                password_error_label['text'] = "Password must contain at least one uppercase letter."
                return False
            if not re.search(r'[a-z]', password):
                password_error_label['text'] = "Password must contain at least one lowercase letter."
                return False
            if not re.search(r'\d', password):
                password_error_label['text'] = "Password must contain at least one digit."
                return False
            if not re.search(r'[@$!%*?&]', password):
                password_error_label['text'] = "Password must contain at least one special character."
                return False
            password_error_label['text'] = ""
            return True

        def validate_confirm_password(password):
            if password != password_entry.get():
                confirm_password_error_label['text'] = "passwords don't match"
                return False
            else:
                confirm_password_error_label['text'] = ""
                return True

        def exist_username(username):
            server.sendall(pickle.dumps({'function': 'exist_username', 'args': username}))
            return pickle.loads(server.recv(1024))

        try:
            background_image = assets.GetImage("Assets\\LoginPage\\SignupPage.jpeg")
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

        confirm_password_entry = tk.Entry(root, font=('Gill Sans Ultra Bold', 20), fg='#CCCCCC', bg="#2D3E45", width=21, borderwidth=0, highlightthickness=0)
        confirm_password_entry.insert(0, 'Confirm Password')
        confirm_password_entry.config(insertofftime=1000000)
        confirm_password_entry.bind('<FocusIn>', lambda event: on_entry_click(event, "Confirm Password", confirm_password_entry))
        confirm_password_entry.bind('<FocusOut>', lambda event: on_focus_out(event, "Confirm Password", confirm_password_entry))
        confirm_password_entry.bind('<KeyRelease>', lambda event: validate_confirm_password(confirm_password_entry.get()))
        confirm_password_entry.bind('<KeyPress>', lambda event: "break" if event.char == " " else None)
        confirm_password_entry.place(x=415, y=612)

        username_error_label = tk.Label(root,text='', font=('Helvetica', 10), fg='#CCCCCC', bg="#2D3E45",borderwidth=0, highlightthickness=0,anchor='e',width=38)
        username_error_label.place(x=650, y=471)

        password_error_label = tk.Label(root,text='', font=('Helvetica', 10), fg='#CCCCCC', bg="#2D3E45", borderwidth=0, highlightthickness=0,anchor='e',width=40)
        password_error_label.place(x=640,y=548)

        confirm_password_error_label = tk.Label(root,text='', font=('Helvetica', 10), fg='#CCCCCC', bg="#2D3E45",borderwidth=0, highlightthickness=0,anchor='e',width=38)
        confirm_password_error_label.place(x=650, y=603)

        def signup():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if password != confirm_password:
                confirm_password_error_label['text'] = "Passwords do not match."
            else:
                confirm_password_error_label['text'] = ""

            server.sendall(pickle.dumps({'function': 'add_user', 'args': (username, password)}))
            response = pickle.loads(server.recv(1024))
            if response:
                pickle.dump((username, password), open('Assets\\cache\\cache.dat', 'wb+'))
                Login(username, password)
                root.destroy()
                print("Signed up successfully")
            else:
                username_error_label['text'] = "Signup failed. Please try again."

        signup_button = tk.Button(root, text="Signup", command=signup, font=('Gill Sans Ultra Bold', 25), fg='white', bg="#2D3E45", width=16, borderwidth=0, highlightthickness=0, activebackground="#2D3E45", activeforeground='black')
        signup_button.place(x=499, y=683)
        confirm_password_entry.bind('<Return>', lambda event: signup())

        def switch_to_login():
            root.destroy()
            Login.login_window()

        login_button = tk.Button(root, text="Have an account? Login", command=switch_to_login, bg='#303040', fg='white', borderwidth=0, relief="flat", activeforeground='#4099FF', activebackground='#303040')
        login_button.place(x=1145, y=745)

        root.mainloop()

    def login_window():
        root = tk.Tk()
        root.title("Login")
        root.attributes('-fullscreen', True)
        root.configure(bg="black")

        def on_entry_click(event,text,object):
            if object.get()==text:
                object.delete(0,"end");object['fg']='#FFFFFF'
                if object==password_entry:object.config(show="*")  

        def on_focus_out(event,text,object):
            if object.get()=='':
                object['fg']='#CCCCCC'
                object.insert(0,text)
                object.config(show="")

        try:
            background_image = assets.GetImage("Assets\\LoginPage\\LoginPage.jpeg")
            root.background_image = background_image
            background_label = tk.Label(root, image=background_image, bg='Black')
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Error loading background image:", e)

        username_entry = tk.Entry(root,font=('Gill Sans Ultra Bold',20),fg='#CCCCCC',bg="#2D3E45", width=21,borderwidth=0,highlightthickness=0)
        username_entry.bind('<FocusIn>', lambda event:on_entry_click(event,"Username",username_entry))
        username_entry.bind('<FocusOut>', lambda event:on_focus_out(event,"Username",username_entry))
        username_entry.insert(0,'Username')
        username_entry.bind('<KeyPress>', lambda event:"break" if event.char == " " else None)
        username_entry.config(insertofftime=1000000)
        username_entry.place(x=416,y=478)

        password_entry = tk.Entry(root, font=('Gill Sans Ultra Bold', 20), fg='#CCCCCC', bg="#2D3E45", width=21, borderwidth=0, highlightthickness=0)
        password_entry.insert(0,'Password')
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
                login_button['font']=('Gill Sans Ultra Bold',20)
                login_button['fg']='Red'
                login_button['text']='Invalid Credentials'
                root.after(1000,error_box)
        login_button = tk.Button(root,text="Login     ",command=login,font=('Gill Sans Ultra Bold',25),fg='white',bg="#2D3E45",width=16,borderwidth=0,highlightthickness=0,activebackground="#2D3E45",activeforeground='black')
        login_button.place(x=499,y=683)
        password_entry.bind('<Return>',lambda event:login())

        def error_box():
            login_button['text']="Login       ";login_button['fg']='White';login_button['font']=('Gill Sans Ultra Bold',25)
        def switch_to_signup():
            root.destroy()
            Login.signup_window()

        signup_button = tk.Button(root, text="Don't have an account? Signup", command=switch_to_signup,bg='#303040',fg='white',borderwidth=0,relief="flat",activeforeground='#4099FF',activebackground='#303040')
        signup_button.place(x=1145,y=745)
        root.mainloop()

class assets:
    def __init__(self):
        assets.LoginPage = ImageTk.PhotoImage(Image.open("Assets\\LoginPage\\LoginPage.jpeg"))
    def GetImage(address = str):
        return ImageTk.PhotoImage(Image.open(address))

username, password = user.check_cache()
Login(username,password)
server.close()
