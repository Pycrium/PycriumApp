import socket
import pickle
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1000

class user:
    IP = {}
    credentials = {}
    currency = {}
    data = {}

    def LoadCredentials():
        try:
            with open('ServerData\\credentials.dat', 'rb') as file:
                user.credentials = pickle.load(file)
        except FileNotFoundError:
            user.credentials = {}

    def SaveCredentials():
        with open('ServerData\\credentials.dat', 'wb+') as file:
            pickle.dump(user.credentials, file)

class Pycrium:
    def __init__(self, client, address):
        print(f'Let Game: {user.IP[address]}')

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

    def login_request(self, client, address, credential):
        try:
            if user.credentials[credential[0]] == credential[1]:
                client.sendall(pickle.dumps(True))
                user.IP[address] = credential[0]
                print(credential[0], 'login success')
                Pycrium(client,address)
            else: raise Exception()
        except:
            client.sendall(pickle.dumps(False))
            self.login(client, address)

    def exist_username(self, client, address, username):
        if username in user.credentials:
            client.sendall(pickle.dumps(False))
        else:
            client.sendall(pickle.dumps(True))
        self.login(client, address)

    def add_user(self, client, address, credential):
        user.credentials.setdefault(credential[0], credential[1])
        user.SaveCredentials()
        client.sendall(pickle.dumps(True))
        self.login(client, address)

user.LoadCredentials()
Lobby(PORT)
