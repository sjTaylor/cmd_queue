import struct
import sys
import select

def encode(code,data):
	if type(data) is str:
		data = bytearray(data)
	size = len(data)
	return struct.pack('ii',code,size) + data

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