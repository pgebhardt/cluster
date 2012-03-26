from multiprocessing import Process


class Node(Process):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(Node, self).__init__()

        # set address
        self.address = address
        self.routerAddress = address.split('.')[0]

        # list of commands
        self.commands = {}

        # register standard commands
        self.register_command('print', self.print_)
        self.register_command('error', self.error)

    def run(self):
        # main loop
        while True:
            # wait for input data
            sender, reciever, message = self.input.recv()

            # check for termination
            if message[0] == 'stop':
                # inform router to delete node
                self.output.put((self.address, self.routerAddress,
                    ('delete node', self.address)))

                # output termination
                print 'terminating node {}'.format(self.address)

                # stop process
                return

            # check correct reciever
            if reciever != self.address:
                self.output.put((self.address, sender,
                    ('wrong reciever', message)))

            else:
                # call on message method
                answer = self.on_message(sender, message)

                # send answer
                if not answer is None:
                    self.output.put((self.address, sender, answer))

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

    def print_(self, sender, string):
        print string

    def error(self, sender, message):
        # output error
        print 'Error: {}'.format(message)

    def start(self, input, output):
        # save input and output
        self.input = input
        self.output = output

        # call base class method
        super(Node, self).start()
