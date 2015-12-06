def drawmap(x,y, pre="  ", you="X", unknown="?", lines=["","",""]):
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
