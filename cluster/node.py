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
        self.running = False

    def start(self, input, output):
        if not self.running:
            # save input and output
            self.input = input
            self.output = output

            # set running flag
            self.running = True

            # call base class method
            super(Node, self).start()

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
                # call request handler
                self.on_request(message)

            elif 'response' in message:
                # call response handler
                self.on_response(message)

            else:
                # TODO
                pass

    def request(self, receiver, responder, request, *args, **kargs):
        # register responder
        if not responder is None:
            self.register_responder(request, receiver, responder)

        # generate message
        message = {'request': request, 'sender': self.address,
            'receiver': receiver, 'args': args, 'kargs': kargs}

        # send request
        self.output.put(message)

    def respond(self, reciever, request, *args, **kargs):
        # generate message
        message = {'sender': self.address, 'receiver': reciever,
            'response': request, 'args': args, 'kargs': kargs}

        # send response
        self.output.put(message)

    def register_responder(self, request, reciever, responder):
        # add responder to dict
        self.responder[(request, reciever)] = responder

    def on_request(self, message):
        # get request
        request = message['request']

        # check for callable attribute
        if hasattr(self, request):
            # check for callable
            if callable(getattr(self, request)):
                # call method
                response = getattr(self, request)(message['sender'],
                    *message['args'], **message['kargs'])

                # send response
                if not response is None:
                    self.respond(message['sender'],
                        message['request'], response)

    def on_response(self, message):
        # get response tuple
        response = (message['response'], message['sender'])

        # try execute responder
        try:
            self.responder[response](message['sender'],
                *message['args'], **message['kargs'])

            # delete responder
            del self.responder[response]

        except:
            # TODO
            pass

    def print_to_screen(self, sender, string):
        print string

        return True

    def stop(self, sender):
        # set running flag
        self.running = False

        return True
