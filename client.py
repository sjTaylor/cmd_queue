import socket
import struct
import sys

args = sys.argv

connection = socket.create_connection(('localhost',12345))
connection.close()