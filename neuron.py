import cluster
import sys
import numpy


class Neuron(cluster.Node):
    def __init__(self, address='-1.-1'):
        # call base class init
        super(Neuron, self).__init__(address)

        # activation
        self.activation = 0

        # threshold
        self.threshold = 0

        # neuron output
        self.neuron_output = 0

        # dict of weights and inputs
        self.weights = {}
        self.inputs = {}

        # list of listener
        self.listener = []

        # register commands
        self.register_command('add predecessor', self.add_predecessor)
        self.register_command('add listener', self.add_listener)
        self.register_command('get output', self.get_output)
        self.register_command('output', self.on_output)
        self.register_command('set threshold', self.set_threshold)
        self.register_command('input', self.input_phase)
        self.register_command('work', self.work_phase)

    def add_predecessor(self, sender, predecessor, weight=1):
        # add to dict
        self.weights[predecessor] = weight
        self.inputs[predecessor] = 0

        # add self as predecessors listener
        self.output.put((sender, predecessor,
            ('add listener', self.address)))

        return ('predecessor added', predecessor, weight)

    def add_listener(self, sender, listener):
        # add listener to list
        self.listener.append(listener)

        return ('listener added', listener)

    def get_output(self, sender):
        # send output
        return ('output', self.neuron_output)

    def on_output(self, sender, output):
        # set predecessor
        self.inputs[sender] = output

    def set_threshold(self, sender, threshold):
        # set threshold
        self.threshold = threshold

        return ('threshold set', threshold)

    def input_phase(self, sender, input=0):
        # set activation to input
        self.activation = input

        # calc output
        self.neuron_output = self.f_out(self.activation)

        # tell all listener new output
        for listener in self.listener:
            self.output.put((self.address, listener,
                ('output', self.neuron_output)))

        return ('output', self.neuron_output)

    def work_phase(self, sender):
        if len(self.weights) > 0:
            # calc net input
            net = 0
            weights = []
            inputs = []
            for predecessor in self.weights:
                weights.append(self.weights[predecessor])
                inputs.append(self.inputs[predecessor])

            print inputs, weights
            net = self.f_net(numpy.array(inputs), numpy.array(weights))
            print net

            # calc new activation
            self.activation = self.f_act(net, self.threshold)
            print self.activation

        # calc new output
        self.neuron_output = self.f_out(self.activation)

        # tell all listener new output
        for listener in self.listener:
            self.output.put((self.address, listener,
                ('output', self.neuron_output)))

        return ('output', self.neuron_output)

    def f_net(self, inputs, weights):
        # calc scalar product of inputs and weights
        return numpy.sum(inputs * weights)

    def f_act(self, net, threshold=0):
        # threshold function
        if net >= threshold:
            return 1.0

        else:
            return 0.0

    def f_out(self, act):
        # identity
        return act


def main():
    # get address
    address = int(sys.argv[1])

    # get port
    port = int(sys.argv[2])

    # get script
    script = None

    if len(sys.argv) == 4:
        # open file
        f = open(sys.argv[3])

        try:
            script = f.read()
        finally:
            f.close()

    # create node
    node = cluster.Shell(address, port)
    node.nodeClasses['Neuron'] = Neuron

    # start node
    node.start(script)


if __name__ == '__main__':
    main()
