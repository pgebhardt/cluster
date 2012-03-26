import cluster
import sys


def main():
    # get address
    address = sys.argv[1]

    # get port
    if len(sys.argv) == 3:
        port = sys.argv[2]

    else:
        port = 3000

    # create node
    node = cluster.Shell(address, port)

    # start node
    node.start()


if __name__ == '__main__':
    main()
