import struct
import sys
import select
import codes
import logging
import json
import os


def get_logger(name):
    logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    log = logging.getLogger(name=name)
    return log


def list_from_file(filename):
    thefile = open(filename, 'r')
    lst = []
    for line in thefile:
        lst.append(line.strip())
    return lst


class VarList:
    def __init__(self, arr=[]):
        self.vals = arr

    def __getitem__(self, index):
        if len(self.vals) is 0:
            return None
        if len(self.vals) <= index:
            return self.vals[-1]
        return self.vals[index]


class ClientInterface:
    def __init__(self, connection, id, config):
        self.con = connection
        self.id = id
        self.cmdid = -1
        self.error = False
        self.initialized = False
        self.config = config

    def initialize(self):
        send(self.con, encode(codes.send_config, (self.id, self.config)))

    def give_cmd(self, number, command):
        self.cmdid = number
        send(self.con, encode(codes.send_cmd, (number, command)))

    def get_status(self):
        pass

    def poll(self):
        a, b, c = select.select([self.con], [], [], 0)
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
    MSGLEN = 4
    trig = False
    while len(msg) < MSGLEN:
        chunk = sock.recv(MSGLEN - len(msg))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        msg = msg + chunk
        if len(msg) >= 4 and not trig:
            MSGLEN = struct.unpack('i', msg[:4])[0] + 4
            trig = True
    return msg


def pad(num, padding):
    s = str(num)
    diff = padding - len(s)
    return '0' * diff + s


def do_dir(prefix, padding, out_type, cmd_number):
    return os.path.join(prefix, pad(cmd_number, padding) + '-' + out_type + '.txt')


def encode(code, data=None):
    ret = struct.pack('i', code)
    json_data = {}
    if code in [codes.send_config]:
        args = data[1]
        json_data = {'client_id': data[0],
                     'working_directory': args.working_directory,
                     'output_prefix': args.output_directory,
                     'padding': args.num_digits,
                     'timeout': args.cmd_timeout}
    if code in [codes.send_cmd]:
        json_data['command'] = data[1]
        json_data['cmd_number'] = data[0]

    if code in [codes.finished]:
        json_data['cmd_number'] = data[0]
        json_data['client_id'] = data[1]
        json_data['return_code'] = data[2]

    json_string = json.dumps(json_data)
    ret += bytearray(json_string.encode('utf-8'))
    ret = struct.pack('i', len(ret)) + ret
    return ret


def decode(stuff):
    stuff = stuff[4:]
    code = struct.unpack('i', stuff[0:4])[0]
    return code, json.loads(stuff[4:].decode('utf-8'))


def getinput():
    ret = []
    stuff = True
    while stuff:
        stuff = False
        kbinput, filler, fillertwo = select.select([sys.stdin], [], [], 0)
        for qq in kbinput:
            ret.append(qq.readline())
            stuff = True
    return ret
