from multiprocessing import Process, Pipe, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
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

        # save ip address
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.port = port

        # create queue manager
        self.queueManager = QueueThread(self.queue, self.port, self.key)

        # list of commands
        self.commands = {}

        # register standard commands
        self.register_command('new node', self.new_node)
        self.register_command('delete node', self.delete_node)
        self.register_command('local nodes', self.local_nodes)
        self.register_command('local node list', self.local_node_list)
        self.register_command('remote nodes', self.remote_nodes)
        self.register_command('routing nodes', self.routing_nodes)
        self.register_command('verbose', self.setVerbose)
        self.register_command('connect', self.connect)
        self.register_command('disconnect', self.disconnect)
        self.register_command('stop', self.stop_)
        self.register_command('unsupported command', self.unsupported_command)
        self.register_command('error', self.error)

    def run(self):
        # start queue manager
        self.queueManager.start()

        # main loop
        while 1:
            # get incoming messages
            sender, reciever, message = self.queue.get()

            # output complete message throughput if in verbose mode
            if self.verbose:
                print "{} sent '{}' to {}".format(sender, message, reciever)

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

            elif sender in self.localnodes or sender in self.remotenodes \
                or sender in self.routingnodes:
                self.queue.put((self.address, sender,
                    ('error', ('not connected', reciever))))

            else:
                # corrupted message
                print 'corrupted message: {}'.format(
                    (sender, reciever, message))

            # check message for termination
            if message[0] == 'router stopped' and sender == self.address:
                print 'terminating router {}'.format(self.address)
                return

    def on_message(self, sender, message):
        # try execute command
        try:
            # check length of message
            if len(message) == 1:
                return self.commands[message[0]](sender)

            elif len(message) == 2:
                return self.commands[message[0]](sender, message[1])

            else:
                return self.commands[message[0]](sender, *message[1:])

        except:
            # answer
            return ('unsupported command', message)

    def register_command(self, command, callable):
        # add command to dict
        self.commands[command] = callable

    def new_node(self, sender, nodeClass=Node):
        # new node address
        localAddress = len(self.localnodes) + 1
        address = '{}.{}'.format(self.address, localAddress)

        # check for used address
        while address in self.localnodes:
            localAddress += 1
            address = '{}.{}'.format(self.address, localAddress)

        # create new Node
        node = nodeClass(address)

        # create node connection
        parent, child = Pipe()

        # save connection
        self.localnodes[address] = parent

        # start node
        node.start(child, self.queue)

        # broadcast list of local nodes
        for router in self.routingnodes:
            # check address
            if router != self.address:
                self.queue.put((self.address, router,
                    ('local node list', self.localnodes.keys())))

        # create answer
        return ('node created', address)

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
        if node in self.localnodes:
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

            # answer
            queue.put((sender, address,
                ('connect', self.address, self.ipAddress,
                    self.port, self.key)))
            queue.put((self.address, address,
                ('local nodes', )))

            # inform about success
            return ('connected to', address)

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

    def stop_(self, sender):
        # inform all connected routing nodes
        for router in self.routingnodes:
            if router != self.address:
                self.routingnodes[router].put((self.address, router,
                    ('disconnect', self.address)))

        # stop all local nodes
        for node in self.localnodes:
            self.localnodes[node].send((self.address, node, ('stop', )))

        # create answer
        return ('router stopped', )

    def unsupported_command(self, sender, command):
        # output error
        self.error(sender, "'{}' not supported by {}".format(
            command, sender))

    def error(self, sender, message):
        # output error
        print 'Error: {}'.format(message)


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
