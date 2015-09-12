import socket
import struct
import select
import codes
from funs import *
from config import *
import os
import sys

config = Config()
config.get_args(sys.argv)

try:
	connection = socket.create_connection((config.server_ip,config.server_port))
except:
	print('could not connect to server')
	exit(1)

running = True


while running:
	readable, foo1, foo2 = select.select([connection],[],[],2)

	for qq in getinput():
		if 'exit' in qq:
			running=False

	for s in readable:
		message = recv(s)
		code,data = decode(message)
		if code == codes.sending_command:
			command = data
			print('--executing :',command)
			return_code = os.system(command + ' > fdsfsisns')
			if return_code is None:
				print('--return_code is ',None)
				return_code = 1
			print('ret val of send:',send(connection,encode(codes.finished,return_code)))
		if code == codes.exit:
			print('--got exit code')
			running=False

connection.shutdown(socket.SHUT_RDWR)
connection.close()
exit(0)