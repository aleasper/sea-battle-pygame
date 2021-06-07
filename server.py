import socket
from _thread import *
import threading as thr
import json
from conf import HOST, PORT
import pickle
import math

from pprint import pprint

class Server:
    def __init__(self):
        self.HOST = HOST
        self.PORT = int(PORT)
        self.server_socket = socket.socket()
        try:
            self.server_socket.bind((self.HOST, self.PORT))

            print('Waiting for a Connection..')
            self.server_socket.listen(2)  # listen for 2 clients
            while True:
                client, address = self.server_socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                start_new_thread(self.threaded_client, (client, thr.current_thread().ident,))

            self.server_socket.close()
        except socket.error as e:
            print(str(e))

    def reinit(self):
        pass

    def handle_data(self, data):
        if 'command' not in data:
            raise Exception('there is no command')

        if data['command'] == 'reinit':
            self.reinit()

    def threaded_client(self, connection, thread_id):
        connection.send(str(thread_id).encode())
        while True:
            raw_data = connection.recv(2048)
            if not raw_data:
                print('Disconnect')
                break
            data = pickle.loads(raw_data)
            res = self.handle_data(data)
            connection.sendall(pickle.dumps(res))
        connection.close()


if __name__ == '__main__':
    server = Server()
