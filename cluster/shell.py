from router import RoutingNode
from node import Node
import readline
from datetime import datetime
import time


class ShellProxy(object):
    def __init__(self, queue, local, remote):
        # call base class init
        super(ShellProxy, self).__init__()

        # save attributes
        self.queue = queue
        self.local = local
        self.remote = remote

    def __getattr__(self, value):
        # request function
        def request(*args, **kargs):
            # request value
            self.queue.put({'sender': self.local,
                'receiver': self.remote, 'request': value,
                'args': args, 'kargs': kargs})

        return request


def requester(queue, local):
    def request(remote):
        return ShellProxy(queue, local, remote)

    return request


class ShellNode(Node):
    def on_response(self, message):
        # report answers
        print "{} answers '{}' to '{}' at {}".format(message['sender'],
            message['args'], message['response'], datetime.now())


class Shell(object):
    def __init__(self, address, port):
        # call base class init
        super(Shell, self).__init__()

        # create router
        self.router = RoutingNode(address, port)

        # save shell address
        self.address = '{}.1'.format(address)

        # add ShellNode to node dict
        self.router.nodeClasses['ShellNode'] = ShellNode

    def start(self, script=None):
        # start router
        self.router.start()

        # add prining node
        self.router.input.put({'sender': self.address,
            'receiver': self.router.address, 'request': 'new_node',
            'args': [ShellNode], 'kargs': {}})

        # wait a bit
        time.sleep(1)

        # split script
        if not script is None:
            scriptLines = script.split('\n')

        # create requester
        request = requester(self.router.input,
            self.address)

        # main loop
        while True:
            if script == None:
                # get commands
                userInput = raw_input('> ')

            elif len(scriptLines) > 0:
                userInput = scriptLines[0]

                # delete first line
                scriptLines.remove(scriptLines[0])

            else:
                script = None
                continue

            # check for exir
            if userInput == 'quit' or userInput == 'exit':
                break

            # parse input
            try:
                eval(userInput, dict(
                    self.router.nodeClasses.items() + \
                        {'request': request}.items()))

            except Exception, e:
                print "invalid input: '{}'".format(userInput)
                print e
                continue

            # wait a bit
            time.sleep(0.5)

        # stop router
        self.router.input.put({'sender': self.address,
            'receiver': self.router.address, 'request': 'stop',
            'args': [], 'kargs': {}})
