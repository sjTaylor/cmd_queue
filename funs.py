import struct
import sys
import select
import codes

def encode(code,data=None):
	ret = struct.pack('i',code)
	if type(data) is str:
		ret += bytearray(data.encode('utf-8'))
	if code in [codes.finished]:
		ret += struct.pack('i',data)
	return ret

def decode(stuff):
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