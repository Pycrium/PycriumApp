import tkinter as tk
from tkinter import ttk
import socket
import pickle

HOST = '192.168.0.110'
__PORT__ = 1000
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.connect((HOST, __PORT__))

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
	username_entry.bind_all('<Key>',lambda event: exist_username())
	signup_button = tk.Button(root, text="Signup", command=signup)
	signup_button.pack()
	def exist_username():
		server.sendall(pickle.dumps({'function':'exist_username','args':username_entry.get()}))
		if pickle.loads(server.recv(1024)):signup_button['state'] = tk.ACTIVE
		else: signup_button['state'] = tk.DISABLED
		
	def signup():
		username = username_entry.get()
		password = password_entry.get()
		confirm_password = confirm_password_entry.get()
		if password == confirm_password:
			server.sendall(pickle.dumps({'function':'exist_username','args':(username,password)}))
			pickle.dump((username,password),open('Pycrium\\cache.dat','wb+'))
			root.destroy()
			print("Logged in successfully")
			
	
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

	def login():
		username = username_entry.get()
		password = password_entry.get()
		if send_credentials(username,password):
			pickle.dump((username,password),open('Pycrium\\cache.dat','wb+'))
			root.destroy()
		else:
			error_label = tk.Label(root, text="Invalid username or password")
			error_label.pack()

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
        if send_credentials(username, password):
            print("Logged in successfully")
        else:
            login_window()
    else:
        login_window()

username, password = check_cache()

join(username,password)

	
server.close()