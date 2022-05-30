#!/usr/bin/python3

import numbers
import sys
import socket
import select
import json
import base64
import csv
import random
from urllib import response
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
users = {}

# return the client_id of a socket or None
def find_client_id (client_sock):
	for id in users:
		if client_sock == users[id]["socket"]:
			return id
	return None


# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue (client_id, data):
	if client_id == None:
		return data
	cipher = AES.new(client_id, AES.MODE_ECB)
	data = str(data).encode("utf-8")
	data = cipher.encrypt(data)
	return base64.b64encode(data)


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue (client_id, data):
	if client_id == None:
		return data
	cipher = AES.new(client_id, AES.MODE_ECB)
	data = base64.b64decode(data)
	data = cipher.decrypt(data)
	return int(data.decode("utf-8"))


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg (client_sock):
	request = recv_dict(client_sock)		# read the client request
	# detect the operation requested by the client
	# execute the operation and obtain the response (consider also operations not available)
	if request["op"] == "START":
		execute = new_client(client_sock, request)
	elif request["op"] == "NUMBER":
		execute = number_client(client_sock, request)
	elif request["op"] == "STOP":
		execute = stop_client(client_sock, request)
	elif request["op"] == "QUIT":
		execute = quit_client(client_sock, request)
	else:
		print(f"[ERROR] Operation not available! ")
		execute = {"op": request["op"], "status": False, "error": "Operation not available!"}
	send_dict(client_sock, execute)			# send the response to the client
	return None


#
# Suporte da criação de um novo jogador - operação START
#
def new_client (client_sock, request):
	client = request["client_id"]		# detect the client in the request
	print("[REQUEST...] detected" + request["client_id"] + " request.")		
	# verify the appropriate conditions for executing this operation
	if request["client_id"] in users:
		print("Client already exists")
		return {"op": "START", "status": False, "error": "Client existente!"}
	
	print("[SUCCESS] The client " + request["client_id"] + " joined the server.")
	
	users.update({
		request["client_id"]: {
			"socket": client_sock,
			"cipher": base64.b64decode(request["cipher"]) if request["cipher"] != None else None, 
			"numbers" : []}
	})		# process the client in the dictionary
	return {"op": "START", "status": True}		# return response message with or without error message




#
# Suporte da eliminação de um cliente
#
def clean_client (client_sock):
	client_id = find_client_id(client_sock)
	if client_id:
		del users[client_id]		# obtain the client_id from his socket and delete from the dictionary
		return True
	return False


#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client (client_sock):
	id = find_client_id(client_sock)		# obtain the client_id from his socket
	if id not in users:
		print(f"[ERROR] Client {id} does not exists!")
		return {"op": "QUIT", "status": False, "error": "Cliente inexistente!"}		# verify the appropriate conditions for executing this operation
	print(f"[QUITTING...] {id} quit.")
	update_file(id, "QUIT")
	clean_client(client_sock)
	return {"op": "QUIT", "status": True}


# process the report file with the QUIT result
# eliminate client from dictionary
# return response message with or without error message


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file ():
	fout = open("report.csv", 'w')
	writer = csv.DictWriter(fout, delimiter=",", fieldbnames=["client_id", "numbers", "min", "max", "result"])
	writer.writeheader()
	return None
# create report csv file with header


#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file (client_id, result):
	op = users[client_id]
	with open("report.csv", 'a') as f:
		writer = csv.writer(f)
		writer.writerow([client_id, op["numbers"], max(op["numbers"]), min(op["numbers"]), result])
	return None
# update report csv file with the result from the client


#
# Suporte do processamento do número de um cliente - operação NUMBER
#
def number_client (client_sock, request):
	id = find_client_id(client_sock)		# obtain the client_id from his socket
	# verify the appropriate conditions for executing this operation
	if id not in users:
		print(f"[ERROR] Client {id} does not exists!")
		return {"op": "NUMBER", "status": False, "error": "Cliente inexistente!"}
	try:
		recv_num = int(decrypt_intvalue(users[id]["cipher"], request["number"]))
		users[id]["numbers"].append(recv_num)
	
	# return response message with or without error message	
		print(f"[NUMBER] Client {id} sent: {request['number']}")
		return {"op": "NUMBER", "status": True}
	except Exception as e:
		print("[ERROR] ", e)
		return {"op": "NUMBER", "status": False, "error": "Erro ao decodificar!"}
	


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client (client_sock, request):
	id = find_client_id(client_sock)	# obtain the client_id from his socket
	# verify the appropriate conditions for executing this operation
	if id not in users:
		print(f"[ERROR] Client {id} does not exists!")
		return {"op": "QUIT", "status": False, "error": "Cliente inexistente! "}
	
	if len(users[id]["numbers"]) == 0:
		print(f"[ERROR] Not enough data!")
		return {"op": "QUIT", "status": False, "error": "Dados insuficientes!"}
	else:
		print(f"[STOP] Client {id} stopped... ")
		update_file(id, request)
		clean_client(client_sock)
		return {"op": "QUIT", "status": True, "min": users[id]["min"], "max": users[id]["max"]}
	


# process the report file with the result
# eliminate client from dictionary
# return response message with result or error message


def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error
	
	if len(sys.agrv) != 2:
		print("[ERROR] Invalid number of arguments!")
		sys.exit(1)
	elif not sys.argv[1].isnumeric():
		print("[ERROR] Invalid port!")
		sys.exit(2)
	elif int(sys.agrv[1]) < 0 or int(sys.argv[1]) > 65535:
		print("[ERROR] Invalid port!")
		sys.exit(2)
	
	port = int(sys.argv[1])

	print("[ONLINE] Servidor ligado!")
	
	server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind (("127.0.0.1", port))
	server_socket.listen (10)

	clients = []
	create_file ()

	while True:
		try:
			available = select.select ([server_socket] + clients, [], [])[0]
		except ValueError:
			# Sockets may have been closed, check for that
			for client_sock in clients:
				if client_sock.fileno () == -1: users.remove (client_sock) # closed
			continue # Reiterate select

		for client_sock in available:
			# New client?
			if client_sock is server_socket:
				newclient, addr = server_socket.accept ()
				clients.append (newclient)
			# Or an existing client
			else:
				# See if client sent a message
				if len (client_sock.recv (1, socket.MSG_PEEK)) != 0:
					# client socket has a message
					##print ("server" + str (client_sock))
					new_msg (client_sock)
				else: # Or just disconnected
					clients.remove (client_sock)
					clean_client (client_sock)
					client_sock.close ()
					break # Reiterate select

if __name__ == "__main__":
	main()
