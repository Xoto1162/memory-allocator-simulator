import os
import matplotlib.pyplot as plt
import networkx as nx
from pygame import mixer

############################################
###      FONCTIONS AUXILIAIRES           ###
############################################

def drawHeader():
    print("                 uuuuuuu                                     _____  .__  .__                        __                                         __               __   ")
    print("             uu$$$$$$$$$$$uu                                /  _  \\ |  | |  |   ____   ____ _____ _/  |_  ___________  _____________  ____    |__| ____   _____/  |_ ")
    print("          uu$$$$$$$$$$$$$$$$$uu                            /  /_\\  \\|  | |  |  /  _ \\_/ ___\\\\__  \\\\   __\\/  _ \\_  __ \\ \\____ \\_  __ \\/  _ \\   |  |/ __ \\_/ ___\\   __\\")
    print("         u$$$$$$$$$$$$$$$$$$$$$u                          /    |    \\  |_|  |_(  <_> )  \\___ / __ \\|  | (  <_> )  | \\/ |  |_> >  | \\(  <_> )  |  \\  ___/\\  \\___|  |  ")
    print("        u$$$$$$$$$$$$$$$$$$$$$$$u                         \\____|__  /____/____/\\____/ \\___  >____  /__|  \\____/|__|    |   __/|__|   \\____/\\__|  |\\___  >\\___  >__|  ")
    print("       u$$$$$$$$$$$$$$$$$$$$$$$$$u                                \\/                      \\/     \\/                    |__|               \\______|    \\/     \\/      ")
    print("       u$$$$$$$$$$$$$$$$$$$$$$$$$u")
    print("       u$$$$$$\"   \"$$$\"   \"$$$$$$u                        Author  : [ Steeven TRONET ]")
    print("       \"$$$$\"      u$u       $$$$\"                        Version : [ 1.0 ]")
    print("        $$$u       u$u       u$$$")
    print("        $$$u      u$$$u      u$$$")
    print("         \"$$$$uu$$$   $$$uu$$$$\"                          [1] Create process")
    print("          \"$$$$$$$\"   \"$$$$$$$\"                           [2] Kill process")
    print("           u$$$$$$$u$$$$$$$u                              [3] Ask for resources")
    print("             u$\"$\"$\"$\"$\"$\"$u                              [4] Free resources")
    print("  uuu        $$u$ $ $ $ $u$$       uuu                    [5] Display queue by resource")
    print(" u$$$$        $$$$$u$u$u$$$       u$$$$                   [6] Display working processes")
    print("  $$$$$uu      \"$$$$$$$$$\"     uu$$$$$$                   [7] Display pending processes")
    print("u$$$$$$$$$$$uu    \"\"\"\"\"    uuuu$$$$$$$$$$                 [8] Display deadlocks")
    print("$$$$\"\"\"$$$$$$$$$$uuu   uu$$$$$$$$$\"\"\"$$$\"                 [9] Display the graph")
    print(" \"\"\"      \"\"$$$$$$$$$$$uu \"\"$\"\"\"")
    print("           uuuu \"\"$$$$$$$$$$uuu                           [e] Exit script    [c] Clear Screen")
    print("  u$$$uuu$$$$$$$$$uu \"\"$$$$$$$$$$$uuu$$$")
    print("  $$$$$$$$$$\"\"\"\"           \"\"$$$$$$$$$$$\"")
    print("   \"$$$$$\"                      \"\"$$$$\"\"")
    print("     $$$\"                         $$$$\"")
    print("")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def drawGraph(G):
    print("Close graph to continue")
    pos = nx.random_layout(G)

    resources = []
    processes = []
    processes_color = []
    for n, d in G.nodes(data=True):
        if (d["type"] == "process"):
            processes += [n]
            if isEmpty(G.successors(n)):
                processes_color += ["#00FF00"]
            else:
                processes_color += ["#FF0000"]
        elif (d["type"] == "resource"):
            resources += [n]

    nx.draw_networkx_nodes(G, pos, nodelist=resources, node_shape='s')
    nx.draw_networkx_nodes(G, pos, nodelist=processes, node_shape='o', node_color=processes_color)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)

    plt.show()


def isEmpty(iterator):
    try:
        next(iterator)
        return False
    except:
        return True


def inputError(G = None):
    print("Error")


def freeResource(process, resource):
    try:
        G.remove_edge(resource, process)
    except:
        print("The process doesn't have this resource")
        return

    reallocateresource(resource)


def reallocateresource(resource):
    if not isEmpty(G.predecessors(resource)):
         process = next(G.predecessors(resource))
         G.add_edge(resource, process)
         G.remove_edge(process, resource)


def deadlock(G):
    num = 0
    P = []
    partition = []
    nodes = {}

    def parcours(v):
        nonlocal num
        nonlocal P
        nonlocal partition
        nonlocal nodes
        nodes[v] = {}
        nodes[v]["num"] = num
        nodes[v]["numAcce"] = num
        num += 1
        P.append(v)
        nodes[v]["dansP"] = True

        for w in G.successors(v):
            if not (w in nodes):
                parcours(w)
                nodes[v]["numAcce"] = min(nodes[v]["numAcce"], nodes[w]["numAcce"])
            elif w in nodes and nodes[w]["dansP"]:
                nodes[v]["numAcce"] = min(nodes[v]["numAcce"], nodes[w]["num"])

        if nodes[v]["numAcce"] == nodes[v]["num"]:
            C = []
            w = P.pop()
            nodes[w]["dansP"] = False
            if G.nodes[w]["type"] == "process":
                C.append(w)
            while w != v:
                w = P.pop()
                nodes[w]["dansP"] = False
                if G.nodes[w]["type"] == "process":
                    C.append(w)
            if len(C) > 1:
                partition.append(C)

    for v in G.nodes():
        if not v in nodes:
            parcours(v)

    return partition


def isPending(p):
    if not isEmpty(G.successors(p)):
        return True
    return False

############################################
###      FONCTIONS PRINCIPALES           ###
############################################

def addProcess(G):
    if len(deadlock(G)) > 0:
        print("Error ! Impossible to add process because deadlock detected")
        return
    G.add_node("P"+str(G.nbProcess), type="process")
    G.nbProcess += 1


def killProcess(G):
    try:
        p = input("Which process do you want to kill ?")
        resources = []
        for r in G.predecessors("P" + str(p)):
            resources += [r]
        for r in resources:
            freeResource("P"+str(p), r)
        G.remove_node("P" + str(p))
    except:
        print("Process not found !")


def askForResources(G):
    if len(deadlock(G)) > 0:
        print("Error ! Impossible to ask for resources because deadlock detected")
        return
    p = input("Which process ?")
    if not G.has_node("P"+str(p)):
        try:
            p = int(p)
        except:
            print("Process name would be an integer")
            return
        print("Process not found !")
        G.add_node("P" + str(p), type="process")
        G.nbProcess = p + 1
        print("Process created")
    if isPending("P"+str(p)):
        print("Error ! Impossible to ask for resources because the process is pending")
        return

    while True:
        r = input("Which resource ? (press s to stop)")
        if str(r) == "s":
            break

        if not G.has_node("R" + str(r)):
            print("resource not found !")
            continue

        # S'il existe deja un arc entre le processus et la resource ou le contraire
        if G.has_edge("P"+str(p), "R"+str(r)) or G.has_edge("R"+str(r), "P"+str(p)):
            continue

        if isEmpty(G.successors("R"+str(r))):
            G.add_edge("R" + str(r), "P" + str(p))
        else:
            G.add_edge("P" + str(p), "R" + str(r))


def freeResources(G):
    p = input("Which process ?")
    if not G.has_node("P"+str(p)):
        print("Process not found !")
        return
    if isPending("P"+p):
        print("Error ! Impossible to free resource because the process is pending")
        return

    r = input("Which resource ?")

    freeResource("P"+str(p), "R"+str(r))


def displayQueueByresource(G):
    r = input("Which resource ?")
    if not G.has_node("R"+str(r)):
        print("resource not found !")
        return

    queue = ""
    for n in G.predecessors("R" + str(r)):
        queue += n + " "

    print("Queue for R" + str(r) + " : " + queue)


def displayWorkingProcesses(G):
    p = ""
    for n, d in G.nodes(data=True):
        if d["type"] == "process" and isEmpty(G.successors(n)):
            p += n + " "
    print("Working processes : " + p)


def displayPendingProcesses(G):
    p = ""
    for n, d in G.nodes(data=True):
        if d["type"] == "process" and not isEmpty(G.successors(n)):
            p += n + " "
    print("Pending processes : " + p)


def displayDeadlocks(G):
    dl = deadlock(G)
    if len(dl) > 0:
        print("Deadlock(s) : ")
        for v in dl:
            print(v)
    else:
        print("No deadlocks")


############################################
###          CODE PRINCIPALE             ###
############################################
clear()

G = nx.DiGraph()
G.nbProcess = 0
G.add_node("R0", type="resource")
G.add_node("R1", type="resource")
G.add_node("R2", type="resource")

mixer.init()
mixer.music.load('music.mp3')
mixer.music.play(-1)

drawHeader()

while(True):
    try:
        i = input("[Allocator:~$")
        i = int(i)
    except:
        i = str(i)
        if i == "e":
            break
        elif i == 'c':
            clear()
            drawHeader()
        continue

    switcher = {
        1: addProcess,
        2: killProcess,
        3: askForResources,
        4: freeResources,
        5: displayQueueByresource,
        6: displayWorkingProcesses,
        7: displayPendingProcesses,
        8: displayDeadlocks,
        9: drawGraph
    }
    func = switcher.get(i, inputError)
    func(G)
