import socket
import struct
import select
import codes
from funs import *
from config import *
import os
import sys
import subprocess

config = Config()
config.get_args(sys.argv)
myid = 0

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
		if code == codes.send_id:
			myid = data
		if code == codes.send_cmd:
			command = data[1]
			cmdnumber = data[0]
			print('--executing :',command)
			sstdout = open(config.output_prefix+'cmd-'+pad(cmdnumber,config.padding)+'-stdout','w')
			sstderr = open(config.output_prefix+'cmd-'+pad(cmdnumber,config.padding)+'-stderr','w')
			return_code = subprocess.call(command,
											shell=True,
											stdout=sstdout,
											stderr=sstderr,
											timeout=config.cmd_timeout)
			sstdout.close()
			sstderr.close()
			if return_code is None:
				print('--return_code is ',None)
				return_code = 1
			#cmd number, client id, return code
			#print('stuff',cmdnumber,'blah',myid,'foo',return_code)
			send(connection,encode(codes.finished,(cmdnumber,myid,return_code)))
		if code == codes.exit:
			print('--got exit code')
			running=False
		else:
			send(connection,encode(codes.idle))

connection.shutdown(socket.SHUT_RDWR)
connection.close()
exit(0)