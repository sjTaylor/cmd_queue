# cmd_queue
### About cmd_queue

cmd_queue is a solution I made to solve the problem of splitting up work across multiple machines on a network (when 
the work can be split up into multiple commands on the command line).

To do this, a server distributes work to clients in the form of commands they need to run 
(e.g. 'some_program --process some_file').


### Software needed

I made this program with Python version 3.4.

While it may work with other versions I have not tested any of them.

### Running the Program

typing 'exit' and hitting enter will queue the server/client to terminate

#### Server

A `command_file` must be prepared ahead of time. A `command_file` is simply a text file with a command that needs to 
be run un each line (see [commands.txt](commands.txt) for an example of this).

run `python3 server.py --help` to see the help message for more info on the rest of the settings.

#### Clients

Run `python3 client.py server_address [--server-port port_number]`

server_address can be an ip address (e.g. 127.0.0.1) or a name (e.g. bigmem01)

### License

Licenced under the MIT Licence
