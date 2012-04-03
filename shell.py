import cluster
import sys


class TestNode(cluster.Node):
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

        # request listener to add self
        self.request(listener, ('add listener', self.address),
            'listener added', responder)

        return ('listener added', listener)


def main():
    # get address
    address = int(sys.argv[1])

    # get port
    if len(sys.argv) == 3:
        port = int(sys.argv[2])

    else:
        port = 3000

    # create node
    node = cluster.Shell(address, port)

    # register TestNode
    node.router.nodeClasses['TestNode'] = TestNode

    # start node
    node.start()


if __name__ == '__main__':
    main()
