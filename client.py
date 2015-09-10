import socket
import struct
import select
import codes
import funs
import os

server_ip   = 'localhost'
server_port = 12345

try:
	connection = socket.create_connection((server_ip,server_port))
except:
	print('could not connect to server')
	exit()

running = True



while running:
	readable, foo1, foo2 = select.select([connection],[],[],2)

	for qq in funs.getinput():
		if 'exit' in qq:
			running=False

	for s in readable:
		message = s.recv(1000)
		code,data = funs.decode(message)
		if code == codes.sending_command:
			command = data
			print('executing :',command)
			os.system(command)
		if code == codes.exit:
			print('got exit code')
			running=False
	#connection.send(funs.encode(codes.idle))




connection.shutdown(socket.SHUT_RDWR)
connection.close()