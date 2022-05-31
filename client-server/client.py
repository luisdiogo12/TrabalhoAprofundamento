#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict
from Crypto.Cipher import AES

numbers = []
cipherkey = None
cipherkey_to_send = None

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, data):
	if cipherkey == None:
		return data
	cipher = AES.new(cipherkey, AES.MODE_ECB)
	data = str(data).encode("utf-8")
	data = cipher.encrypt(data)
	return base64.b64encode(data)


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	if cipherkey == None:
		return data
	cipher = AES.new(cipherkey, AES.MODE_ECB)
	data = base64.b64decode(data)
	data = cipher.decrypt(data)
	return int(data.decode("utf-8"))


# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	if response["status"] == False:
		print("SERVER RESPONSE ERROR")
		client_sock.close()
		sys.exit(3)
	else:
		return None  


# process QUIT operation
def quit_action (client_sock):
	op = sendrecv_dict(client_sock, {"op": "QUIT"})
	validate_response(client_sock,op)
	print(f"Closing...")
	client_sock.close()
	print(f"Closed.")
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
def run_client(c, client_id, server_address, server_port):
    global cipherkey
    global cipherkey_to_send


    while True:
        input_value = input("Safe connection? [yes/no]: ").lower()
        if input_value == 'n' or input_value == 'no':
            # Not safe connection
            operation_start = sendrecv_dict(
                c, {"op": "START", "client_id": client_id, "cipher": None})
            break
        if input_value == 'y' or input_value == 'yes' or input_value == '':
            # Safe connection
            cipherkey = os.urandom(16)
            cipherkey_to_send = str(base64.b64encode(cipherkey), "utf8")
            operation_start = sendrecv_dict(
                c, {"op": "START", "client_id": client_id, "cipher": cipherkey_to_send})
            break
        print("Error:", "Invalid command")
    # Validate response from server
    validate_response(c, operation_start)
    print(f"Client connected to {server_address}:{server_port}")

    # Client continuous sending numbers while 'quit' or 'stop' is not received
    while True:
        input_value = input(
            "Enter an integer or command (quit/stop): ")
        if input_value.lower() == "quit":
            # quit operation
            quit_action(c)
        elif input_value.lower() == "stop":
            # Stop sending numbers
            operation_stop = sendrecv_dict(c, {"op": "STOP"})
            # Validate response from server
            validate_response(c, operation_stop)
            # Print result
            print("Numbers sent: ", str(numbers))
            print("Min ", str(
                decrypt_intvalue(cipherkey, operation_stop["min"])))
            print("Max: ", str(
                decrypt_intvalue(cipherkey, operation_stop["max"])))
            # Disconnect from server
            print(f"Client disconnected from {server_address}:{server_port}")
            c.close()
            sys.exit(0)
        else:
            # send number to server
            try:
                # Convert input to int
                int_value = int(input_value)
                operation_number = sendrecv_dict(
                    c, {"op": "NUMBER", "number": encrypt_intvalue(cipherkey, int_value)})                
                # Validate response from server
                validate_response(c, operation_number)
                # Add number to list
                numbers.append(int_value)
            except ValueError:
                # Error: invalid input - impossible to convert to int
                print("Error:", "Invalid command or input")
                continue

def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error

	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print(f"Usage: python3 client.py <id> <port> [machine]")
		sys.exit(1)
        # verify type of of arguments and eventually print error message and exit with error
	if not (sys.argv[2].isdigit() and int(sys.argv[2]) >= 0):
		print("Usage: port must be a number greater than zero")
		sys.exit(2)


	port = int(sys.argv[2])
	hostname = "localhost" if len(sys.argv) == 3 else sys.argv[3]

	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect ((hostname, port))

	run_client (client_sock, sys.argv[1], hostname, port)

	client_sock.close ()
	sys.exit (0)

if __name__ == "__main__":
    main()
