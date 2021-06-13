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
                    'ships': [],
                    'field': [[{'x': col, 'y': row, 'colored': False} for col in range(10)] for row in range(10)],
                    'move': False
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
            return {'result': True}

        if data['command'] == 'init_ships':
            self.connected[port]['ships'] = data['ships']
            self.connected[port]['ready'] = True

            players_ready = True
            for player_port in self.connected:
                if not self.connected[player_port]['ready']:
                    players_ready = False

            if not players_ready:
                self.connected[port]['move'] = True

            if players_ready:
                print('Players are ready')
                return {'result': True, 'waiting': False}
            else:
                return {'result': True, 'waiting': True}

        if data['command'] == 'is_opponent_ready':
            players_ready = True
            for player_port in self.connected:
                if not self.connected[player_port]['ready']:
                    players_ready = False

            if players_ready:
                print('Players are ready')
                return {'result': True, 'waiting': False}
            else:
                return {'result': True, 'waiting': True}

        if data['command'] == 'send_hit':
            target_player = [self.connected[p] for p in self.connected if p != port][0]
            if self.connected[port]['move']:
                x = data['x']
                y = data['y']
                hit = False
                for ship in target_player['ships']:
                    for coord in ship['coords']:
                        if coord['x'] == x and coord['y'] == y:
                            print('HITED!!!')
                            hit = True

                        for row in target_player['field']:
                            for field in row:
                                if field['x'] == x and field['y'] == y:
                                    field['colored'] = True

                if not hit:
                    print('MISS')
                    self.connected[port]['move'] = False
                    target_player['move'] = True

                return {'result': True, 'hit': hit}

            return {'result': False}

        if data['command'] == 'get_fields':
            target_player = {}
            try:
                target_player = [self.connected[p] for p in self.connected if p != port][0]
            except:
                target_player = {
                    'ready': False,
                    'ships': [],
                    'field': [[{'x': col, 'y': row, 'colored': False} for col in range(10)] for row in range(10)]
                }
            return {
                'result': True,
                'field': self.connected[port]['field'],
                'enemy_field': target_player['field'],
                'enemy_ships': target_player['ships'],
            }

        if data['command'] == 'is_my_turn':
            return {'status': True, 'move': self.connected[port]['move']}







    def threaded_client(self, connection, thread_id, port):
        connection.send(str(thread_id).encode())
        while True:
            raw_data = connection.recv(8192)
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
