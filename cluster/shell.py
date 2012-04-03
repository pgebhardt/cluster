from router import RoutingNode
from node import Node
import readline
from datetime import datetime
import time


class TestNode(Node):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(TestNode, self).__init__(address)

        # listener
        self.listener = []

        # register command
        self.register_command('add listener', self.add_listener)

    def add_listener(self, sender, listener):
        # check for listener
        if listener in self.listener:
            return None

        # add listener
        self.listener.append(listener)

        # responder
        def responder(sender, listener):
            # print success
            print (sender, listener)

        # register responder
        self.register_responder('listener added', listener, responder)

        # let listener add self
        self.output.put((self.address, listener,
            ('add listener', self.address)))

        return ('listener added', listener)


class ShellNode(Node):
    def on_message(self, sender, message):
        # report answers
        print "{} answers: '{}' at {}".format(sender, message,
            datetime.now())


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
