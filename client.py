import socket
import time
import threading

class Game(object):
    """docstring for Game"""
    def __init__(self, debug=False):
        self.connected = False
        self.debug = debug
        explainstr = """
        Welcome to hidnsekonline
        there are two parties in this game, the escapees and the murderer.

        ESCAPEE: you have to find your companion, and decide
        for a spot to hide together (there's a chat).
        But after a while (1 minute) there will be a murderer on the hunt
        for you.

        MURDERER: is somehow psychic because he can read your chat and is
        skilled in reading footprints.

        to move type /left /up /right or /down in chat
        to hide type /hide
        to kill type /kill (one chance or the escapees win)
        to quit type /quit
        """
        print(explainstr)


    def configure(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True
        if self.debug:
            self.serverip = "localhost"
            self.serverport = 2020
            self.username = "player_{}".format(int(time.time())).split()[0]
            print("Username:",self.username)
        else:
            self.serverip =   input("Server adress: [default:localhost] ")
            if len(self.serverip)==0:
                self.serverip = "localhost"
            self.serverport = input("Server port:   [default:2020]      ")
            if len(self.serverport):
                try:
                    self.serverport = int(self.serverport)
                except:
                    self.serverport = 2020
            else:
                self.serverport = 2020
            self.username = input("Username: ").split()[0]
            #self.send("/username {}".format(self.username))
        self.socket.connect((self.serverip,self.serverport))
        self.send("/connect")
        time.sleep(.3)
        self.send("/username {}".format(self.username))

    def connect(self):
        self.type = None
        self.hidden = False
        import random
        while True:
            servermsg = str(self.socket.recv(1024), "utf-8")
            if servermsg.startswith("/waiting "):
                print(servermsg[1:])
                self.send("/ok wait")
                continue
            if servermsg.startswith("/you "):
                self.type = servermsg[5:]
                if self.type == "ESCAPEE":
                    print("game started!\nyou are an ESCAPEE\ntry to find a place to hide with your companion")
                elif self.type == "MURDERER":
                    print("game started!\nyou are the MURDERER\nthe ESCAPEES have 1 minute to hide")
                    time.sleep(55)
                    self.posx = random.randrange(3)
                    self.posy = random.randrange(3)
                    self.printmap()
                else:
                    print("protocol mishab")
                    raise
                continue
            if servermsg.startswith("/youpos ") and self.type and not self.hidden:
                cmd, x, y = servermsg.split()
                self.posx = int(x)
                self.posy = int(y)
                self.printmap()
                command = str(input(">> "))

    def drawmap(self, x,y, pre="  ", you="X", unknown="?", lines=["","",""]):
        m = "\n"
        for ty in range(3):
            for tx in range(3):
                if tx == 0:
                    m += str(pre)
                    m +="["
                else:
                    m +="-["
                if tx == x and ty == y:
                    m += str(you)
                else:
                    m += str(unknown)
                m+= "]"
            if ty == 1:
                m+="\t\t"
                m+=str(lines[1])
            m+="\n"
            if ty < 2:
                m+=str(pre)
                m+=" |   |   |\t\t"
                if ty == 0:
                    m+=str(lines[0])
                if ty == 1:
                    m+=str(lines[2])
                m+="\n"
        return m

    def printmap(self):
        if self.type == "ESCAPEE":
            m = self.drawmap(self.posx, self.posy, lines=["You are at the X","use /left, /right, /up or /down","to move. Find your companion"])
            print(m)

    def send(self, msg):
        self.socket.send(msg.encode("utf-8"))

    def disconnect(self):
        self.send("/disconnect")
        self.socket.close()


def main(args):
    try:
        debug = False
        if len(args)>1:
            debug = args[1]=="debug"
        client = Game(debug)
        client.configure()
        client.connect()
    except KeyboardInterrupt:
        if client.connected:
            client.disconnect()
        sys.exit()

if __name__ == '__main__':
    import sys
    main(sys.argv)
