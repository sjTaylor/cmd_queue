import socket
import select
import struct
import sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('',12345))

server_socket.listen(16)
read_list = [server_socket]


while True:
	readable, writable, errored = select.select(read_list, [], [],1)
	kbinput, filler,fillertwo = select.select([sys.stdin],[],[],0)
	for qq in kbinput:
		x=qq.readline()
		if 'exit' in x:
			exit()

	for s in readable:
		if s is server_socket:
			print("accepting connection")
			client_socket, address = server_socket.accept()
			read_list.append(client_socket)
			print("Connection from", address)
		else:
			data = s.recv(1024)
			if data:
				s.send(data)
			else:
				s.close()
				read_list.remove(s)