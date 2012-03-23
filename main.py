from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import time
import os
import cluster


def main():
    # create RoutingNode
    routingNode1 = cluster.RoutingNode(0)
    routingNode2 = cluster.RoutingNode(200)

    routingNode1.start()
    routingNode2.start()

    # create new node
    routingNode1.queue.put((os.getpid(), 0, ('new node', )))
    routingNode2.queue.put((os.getpid(), 200, ('new node', )))
    routingNode1.queue.put((os.getpid(), 0,
        ('connect', 200, socket.gethostbyname(socket.gethostname()),
        3200)))

    time.sleep(2)

    routingNode1.queue.put((os.getpid(), 200, ('new node', )))
    print routingNode1.ipAddress

    # add shell
    #shell = cluster.Shell(200)

    # start shell
    #shell.start()

    # main loop
    while 1:
        # send data to node
        routingNode1.queue.put((os.getpid(), 1, ('Hallo node 1', )))
        routingNode1.queue.put((os.getpid(), 201, ('Hallo node 101', )))
        routingNode1.queue.put((os.getpid(), 202, ('Hallo node 102', )))

        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
