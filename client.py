import socket
import struct

connection = socket.create_connection(('localhost',12345))
connection.shutdown(socket.SHUT_RDWR)
connection.close()