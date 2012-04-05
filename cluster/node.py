from multiprocessing import Process


class Node(Process):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(Node, self).__init__()

        # set address
        self.address = address
        self.routerAddress = address.split('.')[0]

        # list of responder
        self.responder = {}

        # set running flag
        self.running = True

    def run(self):
        # main loop
        while self.running:
            # wait for input data
            message = self.input.recv()

            # check for correct receiver
            if message['receiver'] != self.address:
                # TODO
                pass

            # check for request
            if 'request' in message:
                # call message handler
                self.on_message(message)

            elif 'response' in message:
                # call response handler
                self.responder[(message['response'], message['sender'])](
                    message['sender'], *message['args'], **message['kargs'])

                # unregister responder
                del self.responder[(message['response'], message['sender'])]

    def request(self, receiver, responder, request, *args, **kargs):
        # register responder
        self.register_responder(request, receiver, responder)

        # generate message
        message = {'request': request, 'sender': self.address,
            'receiver': receiver, 'args': args, 'kargs': kargs}

        # send request
        self.output.put(message)

    def respond(self, reciever, request, *args, **kargs):
        # generate message
        message = {'sender': self.address, 'reciever': reciever,
            'response': request, 'args': args, 'kargs': kargs}

        # send response
        self.output.put(message)

    def register_responder(self, request, reciever, responder):
        # add responder to dict
        self.responder[(request, reciever)] = responder

    def on_message(self, message):
        # get request
        request = message['request']

        # check for callable attribute
        if hasattr(self, request):
            # check for callable
            if callable(getattr(self, request)):
                # call method
                response = getattr(self, request)(*message['args'],
                    **message['kargs'])

                # send response
                self.respond(message['sender'],
                    message['request'], response)

    def print_to_screen(self, string):
        print string

        return None

    def start(self, input, output):
        # save input and output
        self.input = input
        self.output = output

        # call base class method
        super(Node, self).start()

    def stop(self):
        # set running flag
        self.running = False
