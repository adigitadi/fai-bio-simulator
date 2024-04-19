from neural_node import NeuralNode
import math

class InternalNode(NeuralNode):
    def compute_output(self):
        # Compute the output value for the internal node
        self.output_value = math.tanh(sum(self.input_values.values()))
