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

        # list with node connections
        self.nodes = {}

        # create message queue
        self.queue = Queue()

        # create queue manager
        self.queueManager = QueueThread(self.queue, 3000 + address)

    def run(self):
        # start queue manager
        self.queueManager.start()

        # main loop
        while 1:
            # get incoming messages
            sender, reciever, message = self.queue.get()

            # check reciever
            if reciever == self.address:
                self.on_message(sender, message)

            else:
                self.nodes[reciever].send((sender, reciever, message))

    def on_message(self, sender, message):
        # split message
        messages = message.split()

        # create answer
        answer = ''

        # check messages
        if messages[0] == 'newnode':
            # new node address
            address = self.address + len(self.nodes) + 1

            # create new Node
            node = Node(address)

            # create node connection
            parent, child = Pipe()

            # save connection
            self.nodes[address] = parent

            # start node
            node.start(child, self.queue)

            # answer new node address
            answer = str(address)

        elif messages[0] == 'getnodes':
            # create answer
            for key in self.nodes:
                answer = answer + '{} '.format(key)

        elif messages[0] == 'connect':
            # create queue manager
            class QueueManager(BaseManager): pass
            QueueManager.register('get_queue')
            queueManager = QueueManager(address=(
                messages[1], int(messages[2])))

            # connect
            queueManager.connect()
            queue = queueManager.qet_queue()
            print 'connected'


        # answer
        if sender in self.nodes and answer != '':
            self.nodes[sender].send((self.address, sender, answer))


class QueueThread(Thread):
    def __init__(self, queue, port=3000):
        # call base class init
        super(QueueThread, self).__init__()

        # save message queue
        self.queue = queue

        # init queue mananger
        class QueueManager(BaseManager): pass

        QueueManager.register('get_queue', callable=lambda: self.queue)
        self.manager = QueueManager(address=('', port))

    def run(self):
        # get server
        server = self.manager.get_server()

        # start server
        print 'start server'
        server.serve_forever()
