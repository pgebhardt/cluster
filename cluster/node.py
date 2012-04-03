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

        # list of responder
        self.responder = {}

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
        # check for responder
        if (message[0], sender) in self.responder:
            # execute responder
            try:
                # check length of message
                if len(message) == 1:
                    return self.responder[(message[0], sender)](sender)

                elif len(message) == 2:
                    return self.responder[(message[0], sender)](
                        sender, message[1])

                else:
                    return self.responder[(message[0], sender)](
                        sender, *message[1:])

                # delete responder
                del self.responder[(message[0], sender)]

            except:
                # send error message
                return ('error', 'Executing responder', sender, message)

        # check for commands
        elif message[0] in self.commands:
            # execute command
                try:
                    # check length of message
                    if len(message) == 1:
                        return self.commands[message[0]](sender)

                    elif len(message) == 2:
                        return self.commands[message[0]](sender, message[1])

                    else:
                        return self.commands[message[0]](sender, *message[1:])

                except:
                    # send error message
                    return ('error', 'Executing command', message)

        # unsupported command
        else:
            return ('unsupported command', message)

    def register_command(self, command, callable):
        # add command to dict
        self.commands[command] = callable

    def register_responder(self, command, sender, callable):
        # add responder to dict
        self.responder[(command, sender)] = callable

    def request(self, receiver, request, response, responder):
        # register responder
        self.register_responder(response, receiver, responder)

        # send request
        self.output.put((self.address, receiver, request))

    def print_(self, sender, string):
        print string

    def error(self, sender, message):
        # output error
        print '{}: Error: {}'.format(self.address, message)

    def start(self, input, output):
        # save input and output
        self.input = input
        self.output = output

        # call base class method
        super(Node, self).start()
