import os
from funs import *
import codes
import argparse
import logging

log_format = logging.Formatter(fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                               datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('command_file', help='file with commands that need to be served to clients', type=str)
parser.add_argument('-p', '--port', help='port for server to listen on', type=int, default=12345)
parser.add_argument('--working-directory', help='directory commands need to be run from', type=str)
parser.add_argument('--log-file', help='directory commands need to be run from', type=str, default=None)
args = parser.parse_args()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', args.port))

server_socket.listen(16)
read_list = [server_socket]

clients = []
idle_clients = []

last_id = 0
cmd_dex = 0
command_list = list_from_file(args.command_file)

working_directory = args.working_directory
if False:
    working_directory = VarList(list_from_file(working_directory))
else:
    working_directory = VarList([working_directory])

while True:
    readable, writable, errored = select.select(read_list, [], [], 1)

    for qq in getinput():
        if 'exit' in qq:
            exit()

    for s in readable:
        try:
            client_socket, address = server_socket.accept()
            last_id += 1
            clients.append(ClientInterface(client_socket, last_id))
            clients[-1].initialize()
            log.info("new client : id = %s, address = %s" % (clients[-1].id, address))
        except:
            log.info('a potential client could not connect')

    for c in clients:
        try:
            if c.poll():
                message = recv(c.con)
                code, data = decode(message)
                if code in [codes.idle] and cmd_dex < len(command_list):
                    c.give_cmd(cmd_dex, command_list[cmd_dex])
                    cmd_dex += 1
                elif code == codes.disconnecting:
                    log.info('Client ', c.id, 'is disconnecting')
                    clients.remove(c)
                elif cmd_dex == len(command_list):
                    send(c.con, encode(codes.exit))
                    clients.remove(c)
                if code in [codes.finished]:
                    # cmd number, client id, return code
                    log.info('Command : %s finished by client %s with return code %d' % (data[0], data[1], data[2]))
        except:
            log.warning("connection issues with client %d" % c.id)
            log.warning('-Command: %s failed by client %s . Removing it from client list' % (str(c.cmdid), str(c.id)))
            clients.remove(c)

    if len(clients) == 0 and cmd_dex >= len(command_list):
        log.info('commands finished. server exiting')
        os.system('sleep 1s')
        exit()
