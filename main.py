from multiprocessing import Pipe
import cluster
import time


def main():
    # create node
    node = cluster.Node()

    # create pip
    parent, child = Pipe()

    # start node
    node.start(child, None)

    # main loop
    while 1:
        print 'Hello'

        # send data to node
        parent.send((0, -1, 'Hallo du da'))

        # wait
        time.sleep(2)


if __name__ == '__main__':
    main()
