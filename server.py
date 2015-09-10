import socket
import select
import struct
import sys
import funs
import codes
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('',12345))

server_socket.listen(16)
read_list = [server_socket]

clients      = {}
idle_clients = []


command_list_file = open('commands.txt','r')
command_list = []
for line in command_list_file:
	#print(line.strip())
	command_list.append(line.strip())

while True:
	readable, writable, errored = select.select(read_list, [], [],1)

	for qq in funs.getinput():
		if 'exit' in qq:
			exit()

	for s in readable:
		if s is server_socket:
			#print("accepting connection")
			client_socket, address = server_socket.accept()
			read_list.append(client_socket)
			idle_clients.append(client_socket)
			#print("Connection from", address)
		else:
			message = s.recv(1024)
			if message:
				code, data = funs.decode(message)
				#print('recieved',data)
				if code == codes.idle and s not in idle_clients:
					idle_clients.append(s)
				elif code == codes.finished:
					print('--command finished with exit code :',data)

	for s in idle_clients:
		if len(command_list) == 0:
			s.send(funs.encode(codes.exit))
			idle_clients.remove(s)
			read_list.remove(s)
		else:
			print('--sending command :',command_list[0])
			s.send(funs.encode(codes.sending_command,command_list[0]))
			del command_list[0]
	os.system('sleep 1s')
	if len(read_list) == 1 and len(command_list) == 0:
		exit()			