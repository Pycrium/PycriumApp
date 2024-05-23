import pickle

def reload_credentials(username, password):
	with open(f'ServerData\\credentials.dat', 'wb+') as file:
		pickle.dump({username:password}, file)

def check_credentials():
	with open('ServerData\\credentials.dat', 'rb') as file:
		credentials = pickle.load(file)	
		print(credentials)
		
check_credentials()

