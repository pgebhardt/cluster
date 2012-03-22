from multiprocessing import Pipe
from multiprocessing.managers import BaseManager
import socket
import cluster
import time


def main():
    # create node
    node = cluster.Node()

    # create RoutingNode
    routingNode = cluster.RoutingNode(0)
    routingNode.start()

    # create pip
    parent, child = Pipe()

    # create queue manager
    time.sleep(1)

    class QueueManager(BaseManager): pass
    QueueManager.register('get_queue')
    queueManager = QueueManager(address=(
        socket.gethostbyname(socket.gethostname()), 3000))

    # connect
    queueManager.connect()
    queue = queueManager.get_queue()

    # start node
    node.start(child, None)

    # main loop
    while 1:
        print 'Hello'

        # send data to node
        parent.send((0, -1, 'Hallo du da'))
        queue.put((0, 0, 'Jo router'))

        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
