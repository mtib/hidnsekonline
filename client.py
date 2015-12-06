import socket
import time
import threading
from library import drawmap

class Game:
    def __init__(self):
        self.type = None
        self.start = time.time()
        self.modus = "waiting"
        self.chat = ["","","","","","","",""]
    def connect(self, server, username, port=2020):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((server,port))
        self.send(s,"/join {}".format(username))
        if self.receive(s) == "/welcome":
            s.close()
            self.username = username
            self.server = server
            self.port = port
            return True
        else:
            s.close()
            return False
    def getcon(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server,self.port))
        return s
    def send(self, sock, msg):
        sock.send(msg.encode("utf-8"))
    def receive(self, sock, count=2048):
        return str(sock.recv(count), "utf-8")
    def go(self, typ):
        self.type = typ
        self.modus = "hiding"
        if self.type == "MURDERER":
            print("you have to wait for now")
            while True:
                s=self.getcon()
                self.send(s,"/murderer {} wait".format(self.username))
                a=self.receive(s).split()
                if a[0]=="/go":
                    break
                else:
                    time.sleep(3)
        if self.type == "ESCAPEE":
            print("find your partner")
            s=self.getcon()
            self.send(s,"/escapee {} init".format(self.username))
            a=self.receive(s).split()
            print(a)
            if a[0] == "/youpos":
                self.x = int(a[1])
                self.y = int(a[2])

def updateDisplay():
    global g
    while True:
        print("/update")
        print(drawmap(g.x,g.y))
        for line in g.chat:
            print(line)
        print("\n>> ",end="")
        time.sleep(5)

g = Game()

def main(args):
    global g
    if len(args)>1 and args[1]=="debug":
        num = 1
        while not g.connect("localhost","player_{}".format(num)):
            num += 1
    else:
        while not g.connect(input("server: "), input("username: ")):
            print("server didn't answer or didn't allow username")
    print("successfully connected")
    updater = threading.Thread(daemon=True, target=updateDisplay)
    while True:
        time.sleep(.5)
        s = g.getcon()
        print("switching for modus {}".format(g.modus))
        if g.modus == "waiting":
            g.send(s,"/ping {}".format(g.username))
            a = g.receive(s).split()
            if a[0] == "/ping":
                print("waiting for more players [{}/3]".format(a[1]))
                continue
            elif a[0] == "/go":
                g.go(a[1])
            else:
                s=g.getcon()
                g.send(s,"/disconnect {}".format(g.username))
                break
        if g.modus == "hiding" and g.type == "ESCAPEE":
            if not updater.is_alive():
                updater.start()
            cmd = input(">> ")





if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except ConnectionResetError:
        print("the server shut down")
