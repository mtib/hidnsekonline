import socket
import sys
import threading
import time

class Server:
    def __init__(self, port, listen=20):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.listen = listen

    def start(self):
        self.socket.bind(('',self.port))
        self.socket.listen(self.listen)

    def stop(self):
        self.socket.close()

    def accept(self):
        return self.socket.accept()


class Gameserver:
    def __init__(self, port=2020, maxplayer=5):
        self.port = port
        self.server = Server(port, maxplayer)
        self.live = 0
        self.stat = []

    def start(self):
        self.server.start()
        self.running = True
        while self.running:
            try:
                threading.Thread(target=self.handle,args=self.server.accept()).start()
            except Exception as e:
                self.stop()

    def stop(self):
        self.running = False
        time.sleep(2.0)
        self.server.stop()

    def handle(self, conn, addr):
        self.live += 1
        def smsg(msg):
            conn.send(msg.encode("utf-8"))
        connect = str(conn.recv(1024), "utf-8")
        if connect.startswith("/connect"):
            print("new client connected [{}]".format(self.live))
        else:
            print("client using wrong protocol ({}) to connect: \"{}\"".format(addr[0],connect))
            return False
        username = str(conn.recv(1024), "utf-8")
        if username.startswith("/username "):
            username = username[10:]
        else:
            print("client using wrong protocol ({}) for username".format(addr[0]))
            return False
        self.stat.append(username)
        while self.running:
            try:
                if self.live < 3:
                    smsg("/waiting for other players [{}]".format(self.stat))
                    time.sleep(5.0)
                else:
                    pass
            except Exception as e:
                break
        conn.close()
        self.live -= 1

if __name__ == '__main__':
    s = Gameserver(2000)
    threading.Thread(target=s.start).start()
    while True:
        cmd = input("Command: ")
        if cmd == "stat":
            print(s.stat)
        elif cmd == "live":
            print(s.live)
        elif cmd == "kill":
            s.stop()
            del s
            break
    sys.exit()
