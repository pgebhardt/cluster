from router import RoutingNode
from node import Node
import readline
import time
import numpy


class NumpyNode(Node):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(NumpyNode, self).__init__(address)

        # register calc
        self.register_command('calc', self.calc)

    def calc(self, sender):
        # calc array
        return 2 * numpy.ones((5, 5))


class ShellNode(Node):
    def on_message(self, sender, message):
        # report answers
        print '{} answers: {}'.format(sender, message)


class Shell(object):
    def __init__(self, address, port):
        # call base class init
        super(Shell, self).__init__()

        # create router
        self.router = RoutingNode(address, port)

        # save shell address
        self.address = '{}.1'.format(address)

        # add prining node
        self.router.queue.put((self.address, self.router.address,
            ('new node', ShellNode)))

        # start router
        self.router.start()

    def start(self):
        # wait a bit
        time.sleep(1)
        self.router.queue.put((self.address, '1', ('new node', NumpyNode)))

        # main loop
        while True:
            # get commands
            userInput = raw_input('> ')

            # check for exir
            if userInput == 'quit' or userInput == 'exit':
                break

            # parse input
            try:
                recever, message = eval(userInput)

            except:
                print 'invalid input'
                continue

            # send input message to routing node
            self.router.queue.put((self.address,
                recever, message))

            # wait a bit
            time.sleep(0.5)

        # stop router
        self.router.queue.put((self.address,
            self.router.address, ('stop', )))
