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
        self.livecon = {}

    def start(self):
        try:
            self.server.start()
        except OSError as e:
            print("Port or adress already in use!\nTerminating")
            sys.exit()
        self.running = True
        while self.running:
            try:
                threading.Thread(target=self.handle,args=self.server.accept(),daemon=True).start()
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
        connect = str(conn.recv(64), "utf-8")
        if connect.startswith("/connect"):
            toconsole("new client connected [{}]".format(self.live))
        else:
            toconsole("client using wrong protocol ({}) to connect: \"{}\"".format(addr[0],connect))
            self.live -= 1
            return False
        username = str(conn.recv(2048), "utf-8")
        if username.startswith("/username "):
            username = username[10:].split()[0]
        else:
            toconsole("client using wrong protocol ({}) for username".format(addr[0]))
            self.live -= 1
            return False
        toconsole("{} joined the game".format(username))
        self.stat.append(username)
        self.livecon[username]=(conn, self.live)
        self.chat=[]
        if self.live == 3:
            self.giveRoles()
        def move(direc):
            oldx ,oldy = self.positions[username]
            self.field[oldy][oldx]["player"].remove(username)
            oldc = ""
            newc = ""
            if direc=="/left" and oldx>0:
                self.positions[username]=(oldx-1,oldy)
                oldc = "W"
                newc = "o"
            elif direc=="/right" and oldx<2:
                self.positions[username]=(oldx+1,oldy)
                oldc = "O"
                newc = "w"
            elif direc=="/up" and oldy>0:
                self.positions[username]=(oldx,oldy-1)
                oldc = "N"
                newc = "s"
            elif direc=="/down" and oldy<2:
                self.positions[username]=(oldx,oldy+1)
                oldc = "S"
                newc = "n"
            x,y =self.positions[username]
            self.field[oldy][oldx]["history"]+=oldc
            self.field[y][x]["history"]+=newc
            self.field[y][x]["player"].append(username)
            toconsole("{} going left from [{};{}] to [{};{}]".format(username, oldx,oldy,x,y))
            return "/youpos {} {}".format(x,y)
        while self.running:
            try:
                if self.live < 3:
                    smsg("/waiting for other players [{}/3]".format(self.live))
                    time.sleep(.1)
                    if str(conn.recv(1024), "utf-8") == "/ok wait":
                        time.sleep(3.0)
                    else:
                        toconsole(username + " error while waiting")
                        raise Exception
                else:
                    resp = "{} {}".format(str(conn.recv(512), "utf-8"),"/end/")
                    trimr = resp[:-6]
                    toconsole(username + " " + resp)
                    stringhist = ""
                    persadd =""
                    if resp[0]=="/":
                        cmd, arg = resp.split(maxsplit=1)
                        if cmd == "/chat":
                            self.chat.append("/chat {}: {}".format(username ,arg[:-6]))
                        if cmd == "/left" or cmd == "/right" or cmd =="/up" or cmd == "/down":
                            persadd += move(cmd) + "\n"
                        if cmd == "/gotit":
                            pass

                    for line in self.chat[-5:]:
                        stringhist += line + "\n"
                    for name in self.escapee:
                        thisadd = ""
                        if name == username:
                            toconsole("sending own info log to {}".format(name))
                            self.sendto(name, stringhist+persadd)
                        else:
                            toconsole("sending info log to {}".format(name))
                            if self.positions[name] == self.positions[username]:
                                thisadd = "/meet {}\n".format(username)
                            self.sendto(name, stringhist+thisadd)
            except Exception as e:
                toconsole(username + " generic error")
                break
        conn.close()
        del self.livecon[username]
        self.stat.remove(username)
        self.live -= 1
        toconsole("{} left the game".format(username))

    def smsl(self, conn, msg):
        conn.send(msg.encode("utf-8"))

    def giveRoles(self):
        self.field = [[{},{},{}],[{},{},{}],[{},{},{}]]
        self.escapee = []
        self.positions = {}
        import random
        for row in self.field:
            for cell in row:
                cell["history"]=""
                cell["player"]=[]
        for key in self.livecon:
            if self.livecon[key][1] == 1:
                self.smsl(self.livecon[key][0],"/you MURDERER")
                toconsole("{} is MURDERER".format(key))
                self.murderer = [key]
            else:
                scapcon = self.livecon[key][0]
                self.smsl(scapcon,"/you ESCAPEE")
                x=random.randrange(0,3)
                y=random.randrange(0,3)
                self.positions[key]=(x,y)
                self.field[y][x]["player"].append(key)
                self.field[y][x]["history"]+="B"
                toconsole("{} is ESCAPEE in [{};{}]".format(key,x,y))
                self.escapee.append(key)
                time.sleep(.2)
                self.smsl(scapcon, "/youpos {} {}".format(x,y))
                time.sleep(.5)
        self.startround = time.time()
        def tellMurderer(self):
            time.sleep(55)
            self.sendto(self.murderer[0],"/startsoon")
        def checkIfHidden(self):
            time.sleep(60)
            self.sendall("/murdernow")
        #threading.Thread(target=tellMurderer, args=(self),daemon=True).start()
        #threading.Thread(target=checkIfHidden,args=(self),daemon=True).start()



    def sendall(self, msg):
        for key in self.livecon:
            self.smsl(self.livecon[key][0],msg)

    def sendto(self, client, msg):
        for key in self.livecon:
            if key == client:
                self.smsl(self.livecon[key][0],msg)

def toconsole(msg):
    print("{}\nS> ".format(msg), end="")

if __name__ == '__main__':
    s = Gameserver(2020)
    server = threading.Thread(target=s.start, daemon=True)
    server.start()
    helpstr = """
    help
        show this list
    stat
        returns list of all players
    live
        returns number of live connections
    lcon
        returns dictionary of player pos
    kill
        kills the server
    sendall <msg>
        sends the msg to all players
    send <player> <msg>
        sends the msg to player
    newr
        starts new round
    """
    while True:
        try:
            cmd = input("Command: ")
            cml = cmd.split()
            if cml[0] == "stat":
                print(s.stat)
            elif cml[0] == "help":
                print(helpstr)
            elif cml[0] == "live":
                print(s.live)
            elif cml[0] == "kill":
                server.join(.5)
                s.stop()
                del s
                break
            elif cml[0] == "lcon":
                print(s.livecon)
            elif cml[0] == "sendall":
                s.sendall(cmd[8:])
            elif cml[0] == "send":
                s.sendto(cml[1], cml[2])
            elif cml[0] == "newr":
                server.join(.2)
                s.stop()
                time.sleep(1.5)
                del s
                s = Gameserver(2020)
                server = threading.Thread(target=s.start, daemon=True)
                server.start()
        except IndexError:
            print("wrong command")
        except KeyboardInterrupt:
            pass

    sys.exit()
