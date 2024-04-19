from neural_node import NeuralNode

class ActionNode(NeuralNode):
    def compute_output(self):
        # Aggregate and compute the action node's output
        self.output_value = sum(self.input_values.values())
