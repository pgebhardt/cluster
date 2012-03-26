import cluster


def main():
    # create RoutingNode
    routingNode1 = cluster.RoutingNode(100, 3100)
    routingNode1.start()
    print routingNode1.ipAddress

    # add shell
    shell = cluster.Shell(0)

    # start shell
    shell.start()


if __name__ == '__main__':
    main()
