import struct
import sys
import select
import codes
import socket

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


def encode(code,data=None):
	ret = struct.pack('i',code)
	if type(data) is str:
		ret += bytearray(data.encode('utf-8'))
	if code in [codes.finished]:
		ret += struct.pack('i',data)
	ret = struct.pack('i',len(ret)) + ret
	return ret

def decode(stuff):
	stuff = stuff[4:]
	code = struct.unpack('i',stuff[0:4])[0]
	ret = None
	if code in [codes.exit,codes.idle]:
		ret = None
	elif code in [codes.sending_command]:
		ret = stuff[4:].decode('utf-8')
	elif code in [codes.finished]:
		ret = struct.unpack('i',stuff[4:])[0]
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