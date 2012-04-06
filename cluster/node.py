from basicnode import BasicNode


class Node(BasicNode):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(Node, self).__init__(address)

        # set router address
        self.routerAddress = self.address.split('.')[0]

    def print_to_screen(self, sender, string):
        print string

        return True
