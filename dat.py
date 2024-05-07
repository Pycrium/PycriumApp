import pickle
def save_cache(username, password):
	with open(f'Pycrium\\user.dat', 'wb+') as file:
		pickle.dump({username:password}, file)
save_cache('qq','qq')

