import socket
import pickle
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1000
online = {}

try:
    with open('Pycrium\\user.dat', 'rb') as file:
        user = pickle.load(file)
        print(user)
except FileNotFoundError:
    user = {}

def save_cache(object):
    with open('Pycrium\\user.dat', 'wb+') as file:
        pickle.dump(object, file)

class Pycrium:
    def __init__(self, client, address):
        print('Hi')

class Lobby:
    def __init__(self, PORT):
        self.PORT = PORT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((HOST, self.PORT))
            print(f'Created Lobby {HOST} {self.PORT}')
        except:
            print(f'Error creating Lobby with Port:{self.PORT}')
        self.server.listen()
        threading.Thread(target=self.run).start()

    def run(self):
        while True:
            client, address = self.server.accept()
            threading.Thread(target=self.login, args=(client, address)).start()

    def login(self, client, address):
        try:
            data = pickle.loads(client.recv(4048))
            if data['function'] == 'login_request':
                self.login_request(client, address, data['args'])
            elif data['function'] == 'exist_username':
                self.exist_username(client, address, data['args'])
            elif data['function'] == 'add_user':
                self.add_user(client, address, data['args'])
        except:pass

    def login_request(self, client, address, args):
        try:
            if user[args[0]] == args[1]:
                client.sendall(pickle.dumps(True))
                online[address] = args[0]
                print(user[args[0]], 'login success')
                Pycrium(client,address)
            else: raise Exception()
        except:
            client.sendall(pickle.dumps(False))
            self.login(client, address)

    def exist_username(self, client, address, username):
        if username in user.keys():
            client.sendall(pickle.dumps(False))
        else:
            client.sendall(pickle.dumps(True))

    def add_user(self, client, address, args):
        user.setdefault(args[0], args[1])
        save_cache(user)
        client.sendall(pickle.dumps(True))

Lobby(PORT)
