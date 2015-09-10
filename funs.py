import struct
import sys
import select
import codes

def encode(code,data=[]):
	if type(data) is str:
		data = bytearray(data.encode('utf-8'))
	return struct.pack('i',code) + bytearray(data)

def decode(stuff):
	code = struct.unpack('i',stuff[0:4])[0]
	if code in [codes.exit,codes.idle]:
		return (code, None)
	if code in [codes.sending_command]:
		return (code, stuff[4:].decode('utf-8'))
	return (code, stuff[4:].decode('utf-8'))

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