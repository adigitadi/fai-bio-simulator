from organism import Organism

class NeuralNode:
    """Base class for neural nodes"""

    def __init__(self, organism: Organism, identifier: str):
        self.connections = []  # {neural node that is connected to: weight}
        self.organism = organism  # owner of neural nodes
        self.identifier = identifier
        self.input_values = {}  # {source neural node identifier: value of input}
        self.output_value = 0

    def distribute_inputs(self):
        """Distribute output to all connected neural nodes"""
        for conn in self.connections:
            conn["neural_node"].input_values[self.identifier] = self.output_value * conn["weight"]

    def compute_output(self):
        self.output_value = 0
