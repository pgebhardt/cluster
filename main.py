from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import time
import os
import cluster


def main():
    # create RoutingNode
    routingNode1 = cluster.RoutingNode(100)
    routingNode1.start()
    print routingNode1.ipAddress

    # add shell
    shell = cluster.Shell(0)

    # start shell
    shell.start()


if __name__ == '__main__':
    main()
