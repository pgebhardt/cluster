from multiprocessing import Process, Pipe, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from datetime import datetime
import socket
from node import Node


class RoutingNode(Process):
    def __init__(self, address, port=3000, key='bla'):
        # call base class init
        super(RoutingNode, self).__init__()

        # set address
        self.address = '{}'.format(address)

        # save key
        self.key = key

        # verbose mode flag
        self.verbose = False

        # create message queue
        self.queue = Queue()

        # list with node connections
        self.localnodes = {}
        self.remotenodes = {}
        self.routingnodes = {self.address: self.queue}

        # dict of node classes
        self.nodeClasses = {'Node': Node}

        # save ip address
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.port = port

        # create queue manager
        self.queueManager = QueueThread(self.queue, self.port, self.key)

        # list of responder
        self.responder = {}

        # set running flag
        self.running = True

    def start(self):
        if not self.running:
            # start queue mananger
            self.queueManager.start()

            # set running flag
            self.running = True

            # call base class start
            super(RoutingNode, self).start()

    def run(self):
        # main loop
        while self.running:
            # get incoming messages
            message = self.queue.get()

            # output complete message throughput if in verbose mode
            if self.verbose:
                print '{} at {}'.format(message, datetime.now())

            # get reciever
            receiver = message['receiver']

            # check reciever
            if receiver == self.address:
                # check for request
                if 'request' in message:
                    # call message handler
                    self.on_message(message)

                elif 'response' in message:
                    # call response handler
                    self.responder[(message['response'], message['sender'])](
                        message['sender'], *message['args'],
                        **message['kargs'])

                    # unregister responder
                    del self.responder[(message['response'],
                        message['sender'])]

                continue

            # send message
            if receiver in self.localnodes:
                self.localnodes[receiver].send(message)

            elif receiver in self.remotenodes:
                self.remotenodes[receiver].put(message)

            elif receiver in self.routingnodes:
                self.routingnodes[receiver].put(message)

    def request(self, receiver, responder, request, *args, **kargs):
        # register responder
        if not responder is None:
            self.register_responder(request, receiver, responder)

        # generate message
        message = {'request': request, 'sender': self.address,
            'receiver': receiver, 'args': args, 'kargs': kargs}

        # send request
        self.queue.put(message)

    def respond(self, reciever, request, *args, **kargs):
        # generate message
        message = {'sender': self.address, 'reciever': reciever,
            'response': request, 'args': args, 'kargs': kargs}

        # send response
        self.queue.put(message)

    def register_responder(self, request, reciever, responder):
        # add responder to dict
        self.responder[(request, reciever)] = responder

    def on_message(self, sender, message):
        # get request
        request = message['request']

        # check for callable attribute
        if hasattr(self, request):
            # check for callable
            if callable(getattr(self, request)):
                # call method
                response = getattr(self, request)(*message['args'],
                    **message['kargs'])

                # send response
                self.respond(message['sender'],
                    message['request'], response)

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
        parent, child = Pipe()

        # save connection
        self.localnodes[address] = parent

        # start node
        node.start(child, self.queue)

        # broadcast responder
        self.completionCount = len(self.routingnodes) - 1

        def responder(sender, nodes):
            # decrement counter
            self.completionCount -= 1

            # answer completion
            if self.completionCount <= 0:
                # TODO
                return ('node created', address)

        # broadcast list of local nodes
        for router in self.routingnodes:
            # check address
            if router != self.address:
                # request node update
                self.request(router, ('local node list',
                    self.localnodes.keys()), 'nodes connected',
                    responder)

    def delete_node(self, sender, node):
        # stop node if local
        if node in self.localnodes:
            # stop node
            self.localnodes[node].send((self.address, node, ('stop', )))

            # tell all router to delete node
            for router in self.routingnodes:
                if router != self.address:
                    self.routingnodes[router].put(
                        (sender, router, ('delete node', node)))

            # delete node form list
            del self.localnodes[node]

        elif node in self.remotenodes:
            del self.remotenodes[node]

        else:
            return ('error', ('not connected', node))

        # report success
        return ('node deleted', node)

    def local_nodes(self, sender):
        # list of local nodes
        return ('local node list', self.localnodes.keys())

    def local_node_list(self, sender, remoteNodes):
        # add remote nodes to dict
        for node in remoteNodes:
            self.remotenodes[node] = self.routingnodes[sender]

        return ('nodes connected', remoteNodes)

    def remote_nodes(self, sender):
        # list of remote nodes
        return ('remote node list', self.remotenodes.keys())

    def routing_nodes(self, sender):
        # list of routing nodes
        return ('routing node list', self.routingnodes.keys())

    def setVerbose(self, sender, verbose):
        # set verbose mode
        self.verbose = verbose

        # inform sender
        return ('verbose mode set', verbose)

    def broadcast(self, sender, message):
        # send message to all local nodes
        for node in self.localnodes:
            self.localnodes[node].send((sender, node, message))

        # send message to all remote nodes
        for node in self.remotenodes:
            self.remotenodes[node].put((sender, node, message))

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
                answer = ('error', 'unable to connect',
                    (address, ipAddress, port))
                return answer

            # add new remote node
            self.routingnodes[address] = queue

            # responder
            def connect_responder(sender, address):
                pass

            def local_node_responder(sender, nodes):
                # add remote nodes to dict
                for node in nodes:
                    self.remotenodes[node] = self.routingnodes[sender]

            # request connection
            self.request(address, ('connect', self.address,
                self.ipAddress, self.port, self.key), 'connected',
                connect_responder)

            # request local nodes
            self.request(address, ('local nodes', ), 'local node list',
                local_node_responder)

            # inform about success
            return ('connected', address)

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

            # inform remote to disconnect
            self.routingnodes[address].put((self.address, address,
                ('disconnect', self.address)))

            # remove routingnodes
            del self.routingnodes[address]

            # create answer
            return ('disconnected', address)

        else:
            return ('error', ('not connected', address))

    def stop(self, sender):
        # responder
        def responder(sender, response=None):
            # check for router and nodes to be deleted
            if len(self.routingnodes) == 0 and \
                len(self.localnodes) == 0:
                # set running flag
                self.running = False

                print 'router stopped'

        # inform all connected routing nodes
        for router in self.routingnodes:
            if router != self.address:
                self.request(router, responder, 'disconnect', self.address)

        # stop all local nodes
        for node in self.localnodes:
            self.request(node, responder, 'stop')

        # create answer
        return 'stopping router'

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
