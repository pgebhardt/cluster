from multiprocessing import Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from datetime import datetime
import socket
from basicnode import BasicNode
from node import Node


class RoutingNode(BasicNode):
    def __init__(self, address, port=3000, key='bla'):
        # call base class init
        super(RoutingNode, self).__init__('{}'.format(address))

        # save key
        self.key = key

        # verbose mode flag
        self.verbose = False
        # list with node connections
        self.localnodes = {}
        self.remotenodes = {}
        self.routingnodes = {}

        # dict of node classes
        self.nodeClasses = {'Node': Node}

        # save ip address
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.port = port

    def start(self):
        if not self.running:
            # create queue
            queue = Queue()

            # add self to routing node list
            self.routingnodes[self.address] = queue

            # create queue manager
            self.queueManager = QueueThread(queue, self.port, self.key)

            # call base class start
            super(RoutingNode, self).start(queue, queue)

    def run(self):
        # start queue mananger
        self.queueManager.start()

        # main loop
        while self.running:
            # get incoming messages
            message = self.input.get()

            # output complete message throughput if in verbose mode
            if self.verbose:
                print '{} received: {} at {}'.format(self.address,
                    message, datetime.now())

            # get reciever
            receiver = message['receiver']

            # check reciever
            if receiver != self.address:
                # send message
                if receiver in self.localnodes:
                    self.localnodes[receiver].put(message)

                elif receiver in self.remotenodes:
                    self.remotenodes[receiver].put(message)

                elif receiver in self.routingnodes:
                    self.routingnodes[receiver].put(message)

                continue

            # check for request
            if 'request' in message:
                # call request handler
                self.on_request(message)

            elif 'response' in message:
                # call response handler
                self.on_response(message)

            else:
                # TODO
                pass

    def new_node(self, sender, nodeClass=Node):
        # new node address
        localAddress = len(self.localnodes) + 1
        address = '{}.{}'.format(self.address, localAddress)

        # check for used address
        while address in self.localnodes:
            localAddress += 1
            address = '{}.{}'.format(self.address, localAddress)

        try:
            # create new Node
            node = nodeClass(address)
        except:
            print 'geht nicht'
            return

        # create node connection
        queue = Queue()

        # save connection
        self.localnodes[address] = queue

        # start node
        node.start(queue, self.input)

        # broadcast new node
        if len(self.routingnodes) == 1:
            return address

        else:
            self._count = len(self.routingnodes) - 1

            # responder
            def responder(s, remoteNodes):
                # decrement count
                self._count -= 1

                # check for all router respond
                if self._count <= 0:
                    self.respond(sender, 'new_node', address)

            # request new node append
            for router in self.routingnodes:
                if router != self.address:
                    self.request(router, responder, 'add_node',
                        address)

            return None

    def add_node(self, sender, node):
        # check for connected router
        if sender in self.routingnodes:
            # add remote node to list
            self.remotenodes[node] = self.routingnodes[sender]

            return True

        else:
            # TODO
            return False

    def delete_node(self, sender, node):
        # check for connected node
        if node in self.localnodes:
            # responder
            def responder(sender, success):
                # request all router to delete node
                for router in self.routingnodes:
                    if router != self.address:
                        self.request(router, None, 'delete_node',
                            node)

                # delete node
                del self.localnodes[node]

                # respond
                self.respond(sender, 'delete_node', True)

            # request stopping node
            self.request(node, responder, 'stop')

            return None

        elif node in self.remotenodes:
            # delete node from list
            del self.remotenodes[node]

            return True

        else:
            return False

    def local_nodes(self, sender):
        # list of local nodes
        return self.localnodes.keys()

    def remote_nodes(self, sender):
        # list of remote nodes
        return self.remotenodes.keys()

    def routing_nodes(self, sender):
        # list of routing nodes
        return self.routingnodes.keys()

    def set_verbose(self, sender, verbose):
        # set verbose mode
        self.verbose = verbose

        # inform sender
        return verbose

    def broadcast(self, sender, message):
        # send message to all local nodes
        for node in self.localnodes:
            self.localnodes[node].send((sender, node, message))

        # send message to all remote nodes
        for node in self.remotenodes:
            self.remotenodes[node].put((sender, node, message))

        return True

    def connect(self, sender, address, ipAddress, port, key):
        # connect to routing node
        if not address in self.routingnodes:
            try:
                # create queue manager
                class QueueManager(BaseManager):
                    pass
                QueueManager.register('get_queue')
                queueManager = QueueManager(address=(
                    ipAddress, port), authkey=key)

                # connect
                queueManager.connect()
                queue = queueManager.get_queue()
            except:
                # inform about failure
                return (False, 'unable to connect')

            # add new remote node
            self.routingnodes[address] = queue

            # responder
            def node_list_responder(s, nodes):
                # add nodes to remote node list
                for node in nodes:
                    self.remotenodes[node] = self.routingnodes[address]

                # inform success
                self.respond(sender, 'connect', True)

            def connection_responder(s, success):
                # request node list
                self.request(address, node_list_responder, 'local_nodes')

            # request connection to self
            self.request(address, connection_responder, 'connect',
                self.address, self.ipAddress, self.port, self.key)

            return None

        else:
            return (False, 'allready connected')

    def disconnect(self, sender, address):
        # check for correct address
        if address in self.routingnodes and address != self.address:
            # gather all relevant nodes
            toDelete = []
            for node in self.remotenodes:
                if self.remotenodes[node] == self.routingnodes[address]:
                    toDelete.append(node)

            # delete all connected remote nodes
            for node in toDelete:
                # delete node
                del self.remotenodes[node]

            # remove routingnodes
            del self.routingnodes[address]

            # create answer
            return True

        else:
            return  (False, 'not connected')

    def stop(self, sender):
        # responder
        def responder(sender, success):
            del self.localnodes[sender]

            if len(self.localnodes) == 0:
                self.running = False

        # tell all router to disconnect
        for router in self.routingnodes:
            if router != self.address:
                # send custom message
                self.routingnodes[router].put({'sender': self.address,
                    'receiver': router, 'request': 'disconnect',
                    'args': [self.address], 'kargs': {}})

        # send stop to every node
        for node in self.localnodes:
            self.request(node, responder, 'stop')

        # check localnodes
        if len(self.localnodes) == 0:
            self.running = False

        return True

    def error(self, sender, message):
        # output error
        print '{}: Error: {}'.format(self.address, message)


class QueueThread(Thread):
    def __init__(self, queue, port=3000, key='bla'):
        # call base class init
        super(QueueThread, self).__init__()

        # save message queue
        self.queue = queue

        # init queue mananger
        class QueueManager(BaseManager):
            pass

        QueueManager.register('get_queue', callable=lambda: self.queue)
        self.manager = QueueManager(address=('', port), authkey=key)

    def run(self):
        # get server
        server = self.manager.get_server()

        # start server
        server.serve_forever()
