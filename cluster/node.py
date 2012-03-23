from multiprocessing import Process


class Node(Process):
    def __init__(self, address=-1):
        # call base class init
        super(Node, self).__init__()

        # set address
        self.address = address

        # set code
        self.code = "print '{} recieved data from {}: {}'.format(address, sender, message)"

    def run(self):
        # main loop
        while True:
            # wait for input data
            sender, reciever, message = self.input.recv()

            # check for termination
            if message[0] == 'stop':
                print 'terminating node {}'.format(self.address)
                return

            # check correct reciever
            if reciever != self.address:
                self.output.put((self.address, sender,
                    ('wrong reciever', message)))

            else:
                # call on message method
                self.on_message(sender, message)

    def on_message(self, sender, message):
        # check for commands 
        if message[0] == 'set code':
            # set code
            self.code = message[1]

        else:
            # run code
            exec(self.code, {'address': self.address,
                'sender': sender, 'message': message})

    def start(self, input, output):
        # save input and output
        self.input = input
        self.output = output

        # call base class method
        super(Node, self).start()
