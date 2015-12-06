import socket
import sys
import threading
import time
import random

field = [[{},{},{}],[{},{},{}],[{},{},{}]]
players = []
pinfo = {}
murderer = []
escapee = []
hidden = False
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def log(msg):
    print("{}\n>> ".format(msg),end="")

def handle():
    global murderer
    global field
    global pinfo
    global escapee
    global hidden
    global server
    time.sleep(.3)
    log("server running")
    def send(conn, msg):
        conn.send(msg.encode("utf-8"))
    while True:
        conn, addr = server.accept()
        reason = str(conn.recv(2048),"utf-8")
        log(reason)
        rlist = reason.split()
        if rlist[0]=="/join":
            if rlist[1] in players:
                send(conn,"/disconnect")
            else:
                send(conn,"/welcome")
                players.append(rlist[1])
                pinfo[rlist[1]]={"ip":addr[0],"type":None,"last":time.time()}
        if rlist[0]=="/disconnect":
            players.remove(rlist[1])
        if rlist[0]=="/ping":
            if len(players) < 3:
                send(conn,"/ping {}".format(len(players)))
            else:
                if random.randrange(2) == 0 and len(murderer) == 0:
                    send(conn,"/go MURDERER")
                    murderer = [rlist[1]]
                else:
                    send(conn,"/go ESCAPEE")
                    escapee.append(rlist[1])
        if rlist[0]=="/murderer":
            if rlist[2]=="wait":
                if hidden:
                    send(conn, "/go")
                else:
                    send(conn, "/wait")
        if rlist[0]=="/escapee":
            if rlist[2]=="init":
                x = random.randrange(3)
                y = random.randrange(3)
                while len(field[y][x]["players"]):
                    x = random.randrange(3)
                    y = random.randrange(3)
                field[y][x]["players"].append(rlist[1])
                log("{} -> /youpos {} {}".format(rlist[1],x,y))
                send(conn,"/youpos {} {}".format(x,y))
        for p in pinfo:
            if p == rlist[1]:
                pinfo[p]["last"]=0
            else:
                pinfo[p]["last"]+=1
        conn.close()

def clean():
    global field
    global hidden
    global players
    hidden = False
    field = [[{},{},{}],[{},{},{}],[{},{},{}]]
    players = []
    for row in field:
        for cell in row:
            cell["history"]=""
            cell["players"]=[]

def main(args):
    global server
    clean()
    while True:
        try:
            server.bind(('',2020))
            break
        except OSError:
            print("fighting for port 2020")
            time.sleep(2)
    server.listen(20)
    handler = threading.Thread(daemon=True, target=handle)
    handler.start()
    def kill():
        clean()
        handler.join(.2)
        server.close()
    try:
        while True:
            try:
                cmd = input(">> ")
                if cmd == "kill":
                    kill()
                    sys.exit()
                elif cmd == "new":
                    kill()
                    time.sleep(2)
                    main([])
            except KeyboardInterrupt:
                log("\nKeyboardInterrupt")
    except:
        log("killing the server")
        kill()
        print("\n")


if __name__ == '__main__':
    main(sys.argv)
