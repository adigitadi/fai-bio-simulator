import math

# Constants for the world dimensions
DIM_X, DIM_Y = 1000, 1000
# Constants for the simulation steps and generations
STEPS_PER_GEN = 10000
TOTAL_GENS = 5000
# Constant for the population size
POP_SIZE = 10000

# Simulation step initialization
SIMULATION_STEP = 0
# World initialization
WORLD_MATRIX = [[0 for _ in range(DIM_X)] for _ in range(DIM_Y)]

# Genome and gene lengths
LENGTH_GENOME = 24  # Total number of genes in a genome
LENGTH_GENE = 6  # Total number of hex characters in a gene
# Number of bits for encoding source/sink id
ID_BITS_COUNT = 5  
MAX_INNER_NEURON = 3

# Scaling of weights decoded from the genome
MAX_WEIGHT_VAL = 4
# Scaling factor for weights
WEIGHT_SCALING_FACTOR = math.ceil((2 ** (LENGTH_GENE * 4 - 2 * ID_BITS_COUNT - 3)) / MAX_WEIGHT_VAL)

# Mutation rate
MUTATION_RATE = 0.001  # Probability for a bit to flip in genomes (0, 1)

# Sensory radius for creatures
SENSOR_RADIUS_POP = 2
# Long probe distance for creatures
LONG_RANGE_DIST = 24

SHORT_PROBE_DIST = 4
OSC_START_PERIOD = 32

# Colors for different types of neurons in brain graphs
COLORS_NEURON = {"sensory": "#42caff", "internal": "#8a8a8a", "action": "#ffb24d"}

# Available neuron types
NEURON_TYPES = {
    "sensory": (
        "POS_X_AXIS",
        "POS_Y_AXIS",  # Position in world
        "CLOSEST_BOUND_X",
        "CLOSEST_BOUND_X",
        "CLOSEST_BOUND",  # Distance to nearest edge
        "GENETIC_SIMILARITY_FWD",  # Genetic similarity forward
        "PREV_MOVE_DIR_X",
        "PREV_MOVE_DIR_Y",  # Amount of movement in last movement
        "LONG_RANGE_POPULATION_FWD",
        "LONGPROBE_BARRIER_FWD",  # Long look for population/barrier forward
        "POP_DENSITY",
        "POP_DENSITY_FWD",
        "POP_DENSITY_LR",  # Population density
        "OSCILLATOR",  # Oscillator value
        "AGE",
        "BARRIER_FWD",
        "BARRIER_LR",  # Neighborhood barrier distance
        "RANDOM",
    ),
    "internal": tuple("NEURON" + str(i) for i in range(MAX_INNER_NEURON)),
    "action": (
        "MOVE_DIR_X",
        "MOVE_DIR_Y",
        "MOVE_FWD",
        "MOVE_LR",
        "MOVE_RAND",
        "SET_OSC_PERIOD"
    ),
}

# Dimensions of output image of world
IMG_WIDTH, IMG_HEIGHT = DIM_X * 8, DIM_Y * 8

def check_survival(pos_x: int, pos_y: int) -> bool:
    """pos_x and pos_y are the creature's position in world, return true if it survives"""
    return pos_y < 30 and pos_x < 30 # Survives if in corner
