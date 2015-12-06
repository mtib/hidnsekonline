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
chat = ["","","","","","","",""]
WIDTH = 4
HEIGHT = 6

def log(msg):
    print("{}\n>> ".format(msg),end="")

def handle():
    global murderer
    global field
    global pinfo
    global escapee
    global hidden
    global server
    global chat
    global WIDTH
    global HEIGHT
    time.sleep(.3)
    log("server running")
    def send(conn, msg):
        conn.send(msg.encode("utf-8"))
    while True:
        conn, addr = server.accept()
        reason = str(conn.recv(2048),"utf-8")
        if not len(reason):
            conn.close()
            continue
        log(reason)
        rlist = reason.split()
        if rlist[0]=="/join":
            if rlist[1] in players:
                send(conn,"/disconnect")
            else:
                send(conn,"/welcome {} {}".format(WIDTH,HEIGHT))
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
                    pinfo[rlist[1]]["type"]="MURDERER"
                    murderer = [rlist[1]]
                else:
                    send(conn,"/go ESCAPEE")
                    pinfo[rlist[1]]["type"]="ESCAPEE"
                    escapee.append(rlist[1])
        if rlist[0]=="/murderer":
            if rlist[2]=="wait":
                if hidden:
                    send(conn, "/go")
                else:
                    send(conn, "/wait")
        if rlist[0]=="/escapee":
            if rlist[2]=="init":
                x = random.randrange(WIDTH)
                y = random.randrange(HEIGHT)
                while len(field[y][x]["players"]):
                    x = random.randrange(WIDTH)
                    y = random.randrange(HEIGHT)
                field[y][x]["players"].append(rlist[1])
                log("{} -> /youpos {} {}".format(rlist[1],x,y))
                send(conn,"/youpos {} {}".format(x,y))
        if rlist[0]=="/update":
            chm = ""
            for msg in chat[-8:]:
                chm +="{}\n".format(msg)
            send(conn,chm)
        if rlist[0]=="/chat":
            cmd, who, msg = reason.split(maxsplit=2)
            chat.append("{}: {}".format(who,msg))
        if rlist[0] in ["/left","/right","/up","/down"]:
            x,y = 0,0
            t = ""
            log(field)
            for row in field:
                for cell in row:
                    if rlist[1] in cell["players"]:
                        t = (x%WIDTH,y%HEIGHT)
                        log(t)
                    elif [e for e in escapee if e != rlist[1]][0] in cell["players"]:
                        f = (x%WIDTH,y%HEIGHT)
                    x+=1
                y+=1
            oldx ,oldy = t
            n=t
            field[oldy][oldx]["players"].remove(rlist[1])
            oldc = ""
            newc = ""
            if rlist[0]=="/left" and oldx>0:
                n=(oldx-1,oldy)
                oldc = "W"
                newc = "o"
            elif rlist[0]=="/right" and oldx<(WIDTH-1):
                n=(oldx+1,oldy)
                oldc = "O"
                newc = "w"
            elif rlist[0]=="/up" and oldy>0:
                n=(oldx,oldy-1)
                oldc = "N"
                newc = "s"
            elif rlist[0]=="/down" and oldy<(HEIGHT-1):
                n=(oldx,oldy+1)
                oldc = "S"
                newc = "n"
            x,y=n
            field[oldy][oldx]["history"]+=oldc
            field[y][x]["history"]+=newc
            field[y][x]["players"].append(rlist[1])
            log("{} going left from [{};{}] to [{};{}]".format(rlist[1], oldx,oldy,x,y))
            send(conn,"/youpos {} {} {} {}".format(x,y, f[0], f[1]))
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
    field = []
    for y in range(HEIGHT):
        field.append([])
        for x in range(WIDTH):
            field[y].append({"history":"","players":[]})
    players = []

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
