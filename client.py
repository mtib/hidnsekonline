import socket
import time
import threading

class Game(object):
    """docstring for Game"""
    def __init__(self):
        self.serverip = input("Server adress: ")
        self.serverport = input("Server port: [default:2020] ")
        if len(self.serverport):
            try:
                self.serverport = int(self.serverport)
            except:
                self.serverport = 2020
        else:
            self.serverport = 2020
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.serverip,self.serverport))
        self.send("/connect")
        self.username = input("Username: ")
        self.send("/username {}".format(self.username))
        while True:
            servermsg = str(self.socket.recv(1024), "utf-8")
            if servermsg.startswith("/waiting "):
                print(servermsg[1:])

    def send(self, msg):
        self.socket.send(msg.encode("utf-8"))

    def disconnect(self):
        self.send("/disconnect")
        self.socket.close()


def main(args):
    client = Game()

if __name__ == '__main__':
    from sys import argv
    main(argv)
