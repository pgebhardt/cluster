from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import time
import os
import cluster


def main():
    # create RoutingNode
    routingNode1 = cluster.RoutingNode(0)
    routingNode2 = cluster.RoutingNode(100)

    routingNode1.start()
    routingNode2.start()

    # create new node
    routingNode1.queue.put((os.getpid(), 0, ('new node', )))
    routingNode2.queue.put((os.getpid(), 100, ('new node', )))
    routingNode1.queue.put((os.getpid(), 0,
        ('connect', 100, socket.gethostbyname(socket.gethostname()),
        3100)))
    print routingNode1.ipAddress

    # add shell
    shell = cluster.Shell(200)

    # start shell
    shell.start()

    # main loop
    while 1:
        # send data to node
        routingNode1.queue.put((os.getpid(), 1, ('Hallo node 1', )))
        routingNode1.queue.put((os.getpid(), 101, ('Hallo node 101', )))

        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
