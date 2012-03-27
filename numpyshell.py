import cluster
import sys


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

    # connect to client
    node.router.queue.put(('2.1', '2',
        ('connect', '1', '134.147.138.85', 3000, 'bla')))
    #node.router.queue.put(('2.1', '1', ('new node', NumpyNode)))

    # start node
    node.start()


if __name__ == '__main__':
    main()
