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
working_directory = config.target_working_directory
if wd_is_list:
	working_directory = Varlist(list_from_file(working_directory))
else:
	working_directory = Varlist([working_directory])

while True:
	readable, writable, errored = select.select(read_list, [], [],1)

	for qq in getinput():
		if 'exit' in qq:
			exit()

	for s in readable:
		#if s is server_socket:
			#the read list is just goint to handle new connections
		client_socket, address = server_socket.accept()
		last_id+=1
		clients.append(ClientInterface(client_socket,last_id))
		clients[-1].initialize(working_directory[0],config.output_folder)

	for c in clients:
		if c.poll():
			pass
	
	if len(read_list) == 1 and len(command_list) == 0:
		os.system('sleep 1s')
		exit()			