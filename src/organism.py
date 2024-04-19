import random
import math
from bitstring import BitArray
import utils
import constants

class Organism:
    def __init__(self, dna, pos_x, pos_y):
        self.dna = dna
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dir_x = 0
        self.dir_y = 0
        self.oscillator_period = constants.OSC_START_PERIOD

        # Set random direction on initialization
        while self.dir_x == 0 and self.dir_y == 0:
            self.dir_x = random.randint(-1, 1)
            self.dir_y = random.randint(-1, 1)

        # Color is the first and last three hex characters of dna
        self.color = "#" + dna[:3] + dna[-3:]

        # Decoding dna (mRNA)
        action_neurons = set()  # A set of action neurons in the brain, no duplicates
        connections = []  # List of dicts, indicating source, target and weight
        for gene in dna.split(" "):
            bits = bin(int(gene, 16))[2:].zfill(constants.LENGTH_GENE * 4)

            # Decode source neuron
            if bits[0] == "1":
                source_type = "internal"
            else:
                source_type = "sensory"
            source_id = BitArray(bin=bits[1 : constants.ID_BITS_COUNT + 1]).uint % len(
                constants.NEURON_TYPES[source_type]
            )

            # Decode sink neuron
            if bits[constants.ID_BITS_COUNT + 1] == "1":
                sink_type = "action"
            else:
                sink_type = "internal"
            sink_id = BitArray(
                bin=bits[constants.ID_BITS_COUNT + 2 : 2 * constants.ID_BITS_COUNT + 2]
            ).uint % len(constants.NEURON_TYPES[sink_type])

            # Decode weights
            weight = BitArray(bin=bits[2 * constants.ID_BITS_COUNT + 2 :]).int / constants.WEIGHT_SCALING_FACTOR
            if sink_type == "action":
                action_neurons.add(constants.NEURON_TYPES[sink_type][sink_id])
            # Add to the connections list
            connections.append(
                {
                    "from_type": source_type,
                    "from": constants.NEURON_TYPES[source_type][source_id],
                    "to_type": sink_type,
                    "to": constants.NEURON_TYPES[sink_type][sink_id],
                    "weight": weight,
                }
            )

        # Creating the neuron  (rRNA)
        self.neurons = {"sensory": {}, "internal": {}, "action": {}}  # The "brain"
        for action in action_neurons:
            from action_neuron import ActionNode
            self.neurons["action"][action] = ActionNode(self, action)
            children = [self.neurons["action"][action]]

            while len(children) > 0:
                new_children = []
                for child in children:
                    cc = {"neural_node": child, "weight": 0}
                    for c in connections:
                        if c["to"] == child.identifier:
                            cc["weight"] = c["weight"]
                            if c["from"] in self.neurons[c["from_type"]]:
                                # If the neuron is already created, just add the connection
                                self.neurons[c["from_type"]][
                                    c["from"]
                                ].connections.append(cc)
                            else:
                                # Create the neuron
                                if c["from_type"] == "internal":
                                    from internal_neuron import InternalNode
                                    new_neuron = InternalNode(self, c["from"])
                                    # Internal neurons can be a child of other neurons,
                                    # sensory neurons can't
                                    new_children.append(new_neuron)
                                else:
                                    from sensory_neuron import SensingNode
                                    new_neuron = SensingNode(self, c["from"])
                                self.neurons[c["from_type"]][c["from"]] = new_neuron
                                self.neurons[c["from_type"]][
                                    c["from"]
                                ].connections.append(cc)
                            connections.remove(c)
                children = new_children

    def process_brain(self):
        # Calculate the output of action neurons
        for t in self.neurons:
            for n in self.neurons[t]:
                self.neurons[t][n].compute_output()
                self.neurons[t][n].distribute_inputs()

    def perform_actions(self):
        delta_x, delta_y = 0, 0

        for n in self.neurons["action"]:
            output = self.neurons["action"][n].output_value  # This is the raw sum, not scaled
            match n:
                case "MOVE_DIR_X":
                    delta_x += output
                case "MOVE_DIR_Y":
                    delta_y += output
                case "MOVE_FWD":
                    delta_x += self.dir_x
                    delta_y += self.dir_y
                case "MOVE_LR":
                    delta_x -= self.dir_y
                    delta_y += self.dir_x
                case "MOVE_RAND":
                    if output > 0:
                        # Only move randomly if the action neuron is activated
                        delta_x += random.random() * 2 - 1
                        delta_y += random.random() * 2 - 1
                case "SET_OSC_PERIOD":
                    self.oscillator_period = 2.5 + math.exp(3 * (math.tanh(output) + 1))
                case _:
                    raise TypeError(
                        f"Invalid action neuron {self.neurons['action'][n].identifier}"
                    )

        delta_x, delta_y = math.tanh(delta_x), math.tanh(delta_y)  # Turn into a probability (from 0 to 1)
        prob_x, prob_y = random.random() < abs(delta_x), random.random() < abs(delta_y)
        sign_x, sign_y = -1 if delta_x < 0 else 1, -1 if delta_y < 0 else 1
        self.move(prob_x * sign_x, prob_y * sign_y)

    def move(self, delta_x, delta_y):
        # Move the creature in the world
        target_x, target_y = self.pos_x + delta_x, self.pos_y + delta_y
        if utils.is_within_world_limits(target_x, target_y) and constants.WORLD_MATRIX[target_y][target_x] == 0:
            constants.WORLD_MATRIX[self.pos_y][self.pos_x] = 0
            constants.WORLD_MATRIX[target_y][target_x] = self
            self.pos_x += delta_x
            self.pos_y += delta_y
        if (delta_x, delta_y) == (0, 0):
            self.dir_x = delta_x
            self.dir_y = delta_y
