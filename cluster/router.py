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

        # list with node connections
        self.localnodes = {}
        self.remotenodes = {}
        self.routingnodes = {self.address: self.queue}

        # save ip address
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.port = 3000 + address

        # create queue manager
        self.queueManager = QueueThread(self.queue, self.port)

    def run(self):
        # start queue manager
        self.queueManager.start()

        # main loop
        while 1:
            # get incoming messages
            sender, reciever, message = self.queue.get()

            # check reciever
            if reciever == self.address:
                answer = self.on_message(sender, message)

                # create answer
                if not answer is None:
                    sender, reciever, message = reciever, sender, answer

                else:
                    continue

            # send message
            if reciever in self.localnodes:
                self.localnodes[reciever].send((sender, reciever, message))

            elif reciever in self.remotenodes:
                self.remotenodes[reciever].put((sender, reciever, message))

            elif reciever in self.routingnodes:
                self.routingnodes[reciever].put((sender, reciever, message))

    def on_message(self, sender, message):
        # create answer
        answer = None

        # check messages
        if message[0] == 'new node':
            # new node address
            address = self.address + len(self.localnodes) + 1

            # create new Node
            node = Node(address)

            # create node connection
            parent, child = Pipe()

            # save connection
            self.localnodes[address] = parent

            # start node
            node.start(child, self.queue)

            # answer list of local nodes
            print self.routingnodes
            for router in self.routingnodes:
                # check address
                if router != self.address:
                    self.queue.put((self.address, router,
                        ('local node list', self.localnodes.keys())))

        elif message[0] == 'local nodes':
            # list of local nodes
            answer = ('local node list', self.localnodes.keys())

        elif message[0] == 'local node list':
            # add remote nodes to dict
            print message[1]
            for node in message[1]:
                self.remotenodes[node] = self.routingnodes[sender]

        elif message[0] == 'connect':
            # connect to routing node
            if not message[1] in self.routingnodes:
                # create queue manager
                class QueueManager(BaseManager): pass
                QueueManager.register('get_queue')
                queueManager = QueueManager(address=(
                    message[2], message[3]), authkey='bla')

                # connect
                queueManager.connect()
                queue = queueManager.get_queue()

                # add new remote node
                self.routingnodes[message[1]] = queue

                # answer
                queue.put((self.address, message[1],
                    ('connect', self.address, self.ipAddress, self.port)))
                queue.put((self.address, message[1],
                    ('local nodes', )))

        return answer


class QueueThread(Thread):
    def __init__(self, queue, port=3000):
        # call base class init
        super(QueueThread, self).__init__()

        # save message queue
        self.queue = queue

        # init queue mananger
        class QueueManager(BaseManager): pass

        QueueManager.register('get_queue', callable=lambda: self.queue)
        self.manager = QueueManager(address=('', port), authkey='bla')

    def run(self):
        # get server
        server = self.manager.get_server()

        # start server
        server.serve_forever()
