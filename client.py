import socket
import select
import codes
import funs
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('server_ip', type=str)
parser.add_argument('--server_port', type=int, default=12345, required=False)
args = parser.parse_args()

myid = 0

# os.chdir(config.target_working_directory)
output_prefix = None
padding = None

try:
    connection = socket.create_connection((args.server_ip, args.server_port))
except:
    print('could not connect to server', flush=True)
    raise SystemError

running = True
cmd_timeout = None

log = funs.get_logger(__name__)

while running:
    readable, foo1, foo2 = select.select([connection], [], [], 2)

    for qq in funs.getinput():
        if 'exit' in qq:
            running = False
            funs.send(connection, funs.encode(codes.disconnecting))

    for s in readable:
        # try:
            message = funs.recv(s)
            code, data = funs.decode(message)

            json_data = data

            if code == codes.send_config:
                assert 'client_id' in json_data and 'working_directory' in json_data and 'output_prefix' in json_data
                assert 'padding' in json_data and 'timeout' in json_data
                os.chdir(json_data['working_directory'])
                myid = json_data['client_id']
                output_prefix = json_data['output_prefix']
                padding = json_data['padding']
                cmd_timeout = json_data['timeout']

            elif code == codes.send_cmd:
                assert 'command' in json_data and 'cmd_number' in json_data
                command = json_data['command']
                cmdnumber = json_data['cmd_number']
                log.info('Recieved command number : %d' % cmdnumber)
                log.info('--executing : %s' % command)

                log.info('will write out to: |%s|' % funs.do_dir(output_prefix, padding, 'stdout', cmdnumber))
                log.info('will write err to: |%s|' % funs.do_dir(output_prefix, padding, 'stderr', cmdnumber))

                with open(funs.do_dir(output_prefix, padding, 'stdout', cmdnumber), 'w') as sstdout:
                    with open(funs.do_dir(output_prefix, padding, 'stderr', cmdnumber), 'w') as sstderr:
                        return_code = subprocess.call(command,
                                                      shell=True,
                                                      stdout=sstdout,
                                                      stderr=sstderr,
                                                      timeout=cmd_timeout)
                if return_code is None:
                    log.info('--return_code is None')
                    return_code = 1
                # cmd number, client id, return code
                funs.send(connection, funs.encode(codes.finished, (cmdnumber, myid, return_code)))
            if code == codes.exiting:
                log.info('got signal to stop and shut down')
                running = False
            else:
                funs.send(connection, funs.encode(codes.idle))
        # except:
        #     log.error('some issue occured. terminating')
        #     raise SystemExit

# connection.shutdown(socket.SHUT_RDWR)
connection.close()
raise SystemExit
