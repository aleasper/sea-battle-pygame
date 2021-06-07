import socket
import json
import pickle

from conf import HOST, PORT


class NetworkClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = HOST
        self.port = PORT
        self.addr = (self.server, self.port)
        self.id = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None
