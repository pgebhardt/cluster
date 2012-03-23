from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import time
import os
import cluster


def main():
    # create RoutingNode
    routingNode = cluster.RoutingNode(100)
    routingNode.start()

    # connect to remote node
    routingNode.queue.put((0, 100, ('new node', )))
    routingNode.queue.put((0, 100, ('connect', '192.168.55.161', 3000)))

    # main loop
    while 1:
        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
