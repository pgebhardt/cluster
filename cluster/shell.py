from router import RoutingNode
from node import Node
import readline
import time


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

        # add prining node
        self.router.queue.put((-1, self.router.address,
            ('new node', ShellNode)))

        # save shell address
        self.address = '{}.1'.format(address)

        # start router
        self.router.start()

    def start(self):
        # wait a bit
        time.sleep(0.2)

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
                continue

            # send input message to routing node
            self.router.queue.put((self.address,
                recever, message))

            # wait a bit
            time.sleep(0.2)

        # stop router
        self.router.queue.put((self.address,
            self.router.address, ('stop', )))
