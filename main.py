from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import time
import os
import cluster


def main():
    # create RoutingNode
    routingNode = cluster.RoutingNode(0)
    routingNode.start()

    # create queue manager
    time.sleep(1)

    class QueueManager(BaseManager): pass
    QueueManager.register('get_queue')
    queueManager = QueueManager(address=(
        socket.gethostbyname(socket.gethostname()), 3000))

    # connect
    queueManager.connect()
    queue = queueManager.get_queue()

    # create new node
    queue.put((os.getpid(), 0, 'newnode'))

    # main loop
    while 1:
        # send data to node
        queue.put((os.getpid(), 0, 'Jo router'))
        queue.put((os.getpid(), 1, 'Hallo node'))
        queue.put((1, 0, 'getnodes'))

        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
