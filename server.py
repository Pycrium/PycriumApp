import socket, pickle, threading
HOST = socket.gethostbyname(socket.gethostname())
try:user = pickle.loads(open('Pycrium\\user.dat','rb').read());print(user)
except Exception as e:user = {}



def save_cache(object):
	with open(f'Pycrium\\user.dat', 'wb+') as file:
		pickle.dump(object, file)

class Pycrium:
    def __init__(self):
        print('Hi')

class lobby:
    def __init__(self,PORT):
        self.PORT = PORT
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.server.bind((HOST,self.PORT))
            print(f'Created Lobby {HOST} {self.PORT}')
        except:
            print(f'Error creating Lobby with Port:{self.PORT}')
        self.server.listen()
        threading.Thread(target=self.run).start()
    def run(self):
        while True:
            client,address = self.server.accept()
            threading.Thread(target=self.login,args=(client,address)).start()
    def login(self,client,address):
        try:
            data=pickle.loads(client.recv(4048))
            if data['function']=='login_request':self.login_request(client,address,data['args'])
            elif data['function']=='exist_username':self.exist_username(client,address,data['args'])
            elif data['function']=='add_user':self.add_user(client,address,data['args'])
        except:
            self.login(client,address)
    def login_request(self,client,address,arg=('username','password')):
        if user[arg[0]]==arg[1]:
            client.sendall(pickle.dumps(True))
            print(user[arg[0]],'Joined')
        else:
            client.sendall(pickle.dumps(False))
            self.login(client,address)
    def exist_username(self,client,address,username):
        if username in user.keys():
            client.sendall(pickle.dumps(False))
        else:
            client.sendall(pickle.dumps(True))
        self.login(client,address)
    def add_user(self,client,address,args=('username','password')):
        user.setdefault(args[0],args[1])
        save_cache(user)

lobby(1000)
print('DONE')





