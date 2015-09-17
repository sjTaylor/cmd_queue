import struct
import sys
import select
import codes
import socket

class VarList:
	def __init__(self, node=None,fromstr=None,arr=None, type='nope'):
		#need to clean up
		#this is code from a different project
		self.predict = False
		self.vals = []
		self.predict = type is 'yes'
		if node is not None:
			if 'type' in node.attrib:
				self.predict = node.attrib['type'] == 'yes'
			if self.predict:
				for q in node.text.split(','):
					self.vals.append(int(q))
			else:
				for q in node.text.split(','):
					self.vals.append(q)
		elif fromstr is not None:
			for q in node.split(','):
				self.vals.append(q)
		elif arr is not None:
			self.vals=arr

	def __getitem__(self, dex):
		if len(self.vals) is 0:
			return None
		if self.predict:
			return self.getPredictedVal(self.vals,dex)
		return self.getCutoffVal(self.vals,dex)
	def getCutoffVal(self, nums, index):
		if len(nums) <= index:
			return nums[-1]
		return nums[index]
	def getPredictedVal(self, nums, index):
		if index < len(nums):
			return nums[index]
		if len(nums) == 1:
			return nums[0]
		perLevel = nums[-1] - nums[-2]
		diff = index - len(nums) + 1
		return nums[-1] + perLevel*diff


class Client():
	def __init__(self,connection,id):
		self.con=connection
		self.id=id
		self.cmdid = -1
		self.error=False

	def initialize(self):
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