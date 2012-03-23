from multiprocessing import Process


class Node(Process):
    def __init__(self, address=-1):
        # call base class init
        super(Node, self).__init__()

        # set address
        self.address = address

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
        # standart print
        print '{} recieved data from {}: {}'.format(
            self.address, sender, message)

    def start(self, input, output):
        # save input and output
        self.input = input
        self.output = output

        # call base class method
        super(Node, self).start()
