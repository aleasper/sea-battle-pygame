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

        self.connected = {}
        try:
            self.server_socket.bind((self.HOST, self.PORT))

            print('Waiting for a Connection..')
            self.server_socket.listen(2)  # listen for 2 clients
            while True:
                client, address = self.server_socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                self.connected[address[1]] = {
                    'ready': False,
                    'ships': []
                }
                start_new_thread(self.threaded_client, (client, thr.current_thread().ident, address[1],))
                print(self.connected)
            self.server_socket.close()
        except socket.error as e:
            print(str(e))

    def reinit(self):
        pass

    def handle_data(self, data, port):
        if 'command' not in data:
            raise Exception('there is no command')

        if data['command'] == 'reinit':
            self.reinit()

        if data['command'] == 'init_ships':
            self.connected[port]['ships'] = data['ships']
            self.connected[port]['ready'] = True

            players_ready = True
            for player_port in self.connected:
                if not self.connected[player_port]['ready']:
                    players_ready = False
            print('Players are ready: ', players_ready)

    def threaded_client(self, connection, thread_id, port):
        connection.send(str(thread_id).encode())
        while True:
            raw_data = connection.recv(2048)
            if not raw_data:
                print('Disconnect')
                del self.connected[port]
                print(self.connected)
                break
            data = pickle.loads(raw_data)
            res = self.handle_data(data, port)
            connection.sendall(pickle.dumps(res))
        connection.close()


if __name__ == '__main__':
    server = Server()
