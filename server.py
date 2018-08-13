import os
import funs
import codes
import argparse
import socket
import select

log = funs.get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('command_file', help='file with commands that need to be served to clients '
                                         '(one command per line in text file)', type=str)
parser.add_argument('-p', '--port', help='port for server to listen on', type=int, default=12345)
parser.add_argument('--working-directory', help='directory commands need to be run from '
                                                '(clients will change to the given directory before executing commands)'
                    , type=str, required=True)

parser.add_argument('--output-directory', help='directory to store output for commands (stdout and stderr)',
                    type=str, required=True)
parser.add_argument('--cmd-timeout', help='timeout for commands (in seconds). If a command takes longer than the '
                                          'specified time to run, client will terminate execution and report the '
                                          'return code to the server.', type=int, default=60)
parser.add_argument('--num-digits', help='number of digits for cmd output files. padded with zeros if number of digits '
                                         'is less than num_digits (e.g. if num_digits=5 then 12 -> 000012', type=int,
                    default=4)
args = parser.parse_args()

args.output_directory = os.path.abspath(args.output_directory)
log.info('cmd output will be stored in |%s|' % args.output_directory)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(('', args.port))

    server_socket.listen(16)
    read_list = [server_socket]

    clients = []
    idle_clients = []

    last_id = 0
    cmd_dex = 0
    command_list = funs.list_from_file(args.command_file)

    running = True

    while running:
        readable, writable, errored = select.select(read_list, [], [], 1)

        for qq in funs.getinput():
            if 'exit' in qq:
                raise SystemExit

        for s in readable:
            try:
                client_socket, address = server_socket.accept()
                last_id += 1
                clients.append(funs.ClientInterface(client_socket, last_id, config=args))
                clients[-1].initialize()
                log.info("new client : id = %s, address = %s" % (clients[-1].id, address))
            except:
                import sys
                print("Unexpected error:", sys.exc_info()[0], 'for client', address)
                log.info('a potential client could not connect')

        for c in clients:
            try:
                if c.poll():
                    message = funs.recv(c.con)
                    code, data = funs.decode(message)

                    json_data = data

                    if code in [codes.idle] and cmd_dex < len(command_list):
                        c.give_cmd(cmd_dex, command_list[cmd_dex])
                        cmd_dex += 1
                    elif code == codes.disconnecting:
                        log.info('Client ', c.id, 'is disconnecting')
                        clients.remove(c)
                    elif cmd_dex == len(command_list):
                        funs.send(c.con, funs.encode(codes.exiting))
                        clients.remove(c)
                    if code in [codes.finished]:
                        # cmd number, client id, return code
                        assert 'cmd_number' in json_data and 'client_id' in json_data and 'return_code' in json_data
                        log.info('Command : %s finished by client %s with return code %d' % (json_data['cmd_number'],
                                                                                             json_data['client_id'],
                                                                                             json_data['return_code']))
            except:
                log.warning("connection issues with client %d" % c.id)
                log.warning('-Command: %s failed by client %s . Removing it from client list' % (str(c.cmdid), str(c.id)))
                clients.remove(c)

        if len(clients) == 0 and cmd_dex >= len(command_list):
            log.info('commands finished. server exiting')
            os.system('sleep 1s')
            running = False
