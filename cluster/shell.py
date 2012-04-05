from router import RoutingNode
from node import Node
import readline
from datetime import datetime
import time


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

        # add prining node
        self.router.queue.put({'sender': self.address,
            'receiver': self.router.address, 'request': 'new_node',
            'args': [ShellNode], 'kargs': {}})

        # add ShellNode to node dict
        self.router.nodeClasses['ShellNode'] = ShellNode

    def start(self, script=None):
        # start router
        self.router.start()

        # wait a bit
        time.sleep(1)

        # split script
        if not script is None:
            scriptLines = script.split('\n')

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
                receiver, request, args = eval(userInput, self.router.nodeClasses)

            except:
                print "invalid input: '{}'".format(userInput)
                continue

            # send input message to routing node
            self.router.queue.put({'sender': self.address,
                'receiver': receiver, 'request': request,
                'args': args, 'kargs': {}})

            # wait a bit
            time.sleep(0.5)

        # stop router
        self.router.queue.put({'sender': self.address,
            'receiver': self.router.address, 'request': 'stop',
            'args': [], 'kargs': {}})
