#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from xmlrpc import client
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	if response["status"] == False:
		print("Invalid Status!")
		client_sock.close()
		sys.exit(3)
	else:
		return None


# process QUIT operation
def quit_action (client_sock):
	print(f"QUITTING...")
	client_sock.close()
	sys.exit(4)

# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte da execução do cliente
#
def run_client (client_sock, client_id):
	# "op" =  START
	start =  sendrecv_dict(client_sock, {"op" : "START", "client_id" : client_id})
	validate_response(client_sock, start)
	# WELCOME TEXT
	print("WELCOME USER: " + client_id)

	while 1:
		inputNumber = input("Write a number or 'quit' to end process")
		if inputNumber == "quit" or inputNumber == "QUIT" or inputNumber == "Quit":
			break
		if inputNumber.isnumeric():
			# "op" = NUMBER
			number = sendrecv_dict(client_sock, {"op": "NUMBER", "number": int(inputNumber)})
			validate_response(client_sock, number)
			if 

		return None
	
	# "op" = QUIT
	quit = sendrecv_dict(client_sock, {"op": "QUIT"})
	validate_response(client_sock, quit)
	quit_action(client_sock)	

def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error

	port = ?
	hostname = ?

	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect ((hostname, port))

	run_client (client_sock, sys.argv[1])

	client_sock.close ()
	sys.exit (0)

if __name__ == "__main__":
    main()
