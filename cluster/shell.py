from multiprocessing import Pipe
from router import RoutingNode
from node import Node
import readline
import time


class Shell(object):
    def __init__(self, address):
        # call base class init
        super(Shell, self).__init__()

        # create router
        self.router = RoutingNode(address)

        # create connection
        parent, self.input = Pipe()

        # add connection
        self.router.localnodes[self.router.address + 1] = parent
        self.address = self.router.address + 1

        # add prining node
        self.router.queue.put((self.address, self.router.address,
            ('new node', )))

        # start router
        self.router.start()

    def start(self):
        # main loop
        while True:
            # get commands
            userInput = input('> ')
            recever, message = userInput

            # send input message to routing node
            self.router.queue.put((self.address + 1, recever, message))

            # wait a bit
            time.sleep(0.2)
