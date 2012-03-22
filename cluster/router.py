from multiprocessing import Process, Pipe, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
import socket
from node import Node


class RoutingNode(Process):
    def __init__(self, address):
        # call base class init
        super(RoutingNode, self).__init__()

        # set address
        self.address = address

        # create message queue
        self.queue = Queue()

        # create queue manager
        self.queueManager = QueueThread(self.queue)

    def run(self):
        # start queue manager
        self.queueManager.start()

        # main loop
        while 1:
            # get incoming messages
            sender, reciever, message = self.queue.get()

            print (sender, reciever, message)


class QueueThread(Thread):
    def __init__(self, queue):
        # call base class init
        super(QueueThread, self).__init__()

        # save message queue
        self.queue = queue

        # init queue mananger
        class QueueManager(BaseManager): pass

        QueueManager.register('get_queue', callable=lambda: self.queue)
        self.manager = QueueManager(address=('', 3000))

    def run(self):
        # get server
        server = self.manager.get_server()

        # start server
        print 'start server'
        server.serve_forever()
