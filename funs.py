import struct
import sys
import select
import codes
import socket

def list_from_file(filename):
	thefile = open(filename,'r')
	lst = []
	for line in thefile:
		lst.append(line.strip())
	return lst

class VarList:
	def __init__(self,arr=[]):
		self.vals = arr

	def __getitem__(self, index):
		if len(self.vals) is 0:
			return None
		if len(self.vals) <= index:
			return self.vals[-1]
		return self.vals[index]		


class ClientInterface():
	def __init__(self,connection,id):
		self.con=connection
		self.id=id
		self.cmdid = -1
		self.error=False
		self.initialized = False

	def initialize(self,wd=None,od=None,to=None):
		send(self.con,encode(codes.send_id,self.id))
		#send(self.con,encode(codes.send_wd,wd))
		#send(self.con,encode(codes.send_od,od))
		#send(self.con,encode(codes.send_to,to))

	def give_cmd(self,number,command):
		self.cmdid=number
		send(self.con, encode(codes.send_cmd,(number,command)))

	def get_status(self):
		pass

	def poll(self):
		a,b,c = select.select([self.con],[],[],0)
		return len(a) > 0


def send(soc, msg):
	totalsent = 0
	MSGLEN = len(msg)
	while totalsent < MSGLEN:
		sent = soc.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent
	return totalsent

def recv(sock):
	msg = b''
	MSGLEN=4
	trig = False
	while len(msg) < MSGLEN:
		chunk = sock.recv(MSGLEN-len(msg))
		if chunk == b'':
			raise RuntimeError("socket connection broken")
		msg = msg + chunk
		if len(msg) >= 4 and not trig:
			MSGLEN = struct.unpack('i',msg[:4])[0] + 4
			trig=True
	return msg

def pad(num,padding):
	s = str(num)
	diff = padding-len(s) 
	return '0'*diff + s

def encode(code,data=None):
	ret = struct.pack('i',code)
	if type(data) is str or code in [codes.send_wd,codes.send_od]:
		ret += bytearray(data.encode('utf-8'))
	if code in [codes.send_id]:
		ret += struct.pack('i',data)
	if code in [codes.send_to]:
		ret += struct.pack('f',data)
	if code in [codes.send_cmd]:
		ret += struct.pack('i',data[0])
		ret += bytearray(data[1].encode('utf-8'))
	if code in [codes.finished]:
		ret += struct.pack('iii',data[0],data[1],data[2])
	ret = struct.pack('i',len(ret)) + ret
	return ret

def decode(stuff):
	stuff = stuff[4:]
	code = struct.unpack('i',stuff[0:4])[0]
	ret = None
	if code in [codes.exit,codes.idle]:
		ret = None
	elif code in [codes.send_id]:
		ret = struct.unpack('i',stuff[4:])[0]
	elif code in [codes.send_cmd]:
		ret = []
		ret.append(struct.unpack('i',stuff[4:4+4])[0])
		ret.append(str(stuff[4+4:].decode('utf-8')))
	elif code in [codes.finished]:
		ret = struct.unpack('iii',stuff[4:])
	else:
		ret = stuff[4:].decode('utf-8')
	return (code, ret)

def getinput():
	ret   = []
	stuff = True
	while stuff:
		stuff=False
		kbinput, filler,fillertwo = select.select([sys.stdin],[],[],0)
		for qq in kbinput:
			ret.append(qq.readline())
			stuff=True
	return ret