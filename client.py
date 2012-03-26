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
    node = cluster.RoutingNode(address, port)

    # start node
    node.start()


if __name__ == '__main__':
    main()
