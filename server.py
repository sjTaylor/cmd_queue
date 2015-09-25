import socket
import select
import struct
import sys
from funs import *
from config import *
import codes
import os

config = Config()
config.get_args(sys.argv)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('',config.server_port))

server_socket.listen(16)
read_list = [server_socket]

clients      = []
idle_clients = []

last_id = 0
cmd_dex = 0
command_list = list_from_file(config.cmd_file)
print('cmd_list',command_list)

working_directory = config.target_working_directory
if config.wd_is_list:
	working_directory = VarList(list_from_file(working_directory))
else:
	working_directory = VarList([working_directory])

while True:
	readable, writable, errored = select.select(read_list, [], [],1)

	for qq in getinput():
		if 'exit' in qq:
			exit()

	for s in readable:
		client_socket, address = server_socket.accept()
		last_id+=1
		clients.append(ClientInterface(client_socket,last_id))
		clients[-1].initialize()

	for c in clients:
		if c.poll():
			message = recv(c.con)
			code,data = decode(message)
			if code in [codes.idle] and cmd_dex < len(command_list):
				c.give_cmd(cmd_dex,command_list[cmd_dex])
				cmd_dex+=1
			elif cmd_dex == len(command_list):
				send(c.con,encode(codes.exit))
				clients.remove(c)
			if code in [codes.finished]:
				#cmd number, client id, return code
				print("Command :",data[0],'finished by client',data[1],'with return code',data[2])
	
	if len(clients) == 0 and cmd_dex >= len(command_list):
		print('commands finished.\nserver exiting')
		os.system('sleep 1s')
		exit()