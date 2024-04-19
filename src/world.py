import random
from organism import Organism
import utils
import cv2
import constants as con
import numpy as np

def initialize_environment():
    #Setup the initial environment
    con.WORLD_MATRIX = [[0 for _ in range(con.DIM_X)] for _ in range(con.DIM_Y)]
    con.SIMULATION_STEP = 0

def populate_creatures(population: list[Organism] = []):
    #Populate the world with creatures from the given population or with random genomes if population is empty
    if len(population) == 0:
        for _ in range(con.POP_SIZE):
            x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)
            #print("X is "+str(x)+"Y is "+str(y))
            while con.WORLD_MATRIX[y][x] != 0:
                x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)
            con.WORLD_MATRIX[y][x] = Organism(utils.create_random_dna_sequence(), x, y)
    else:
        for organism in population:
            x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)
            while con.WORLD_MATRIX[y][x] != 0:
                x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)
            con.WORLD_MATRIX[y][x] = organism
            organism.x = x
            organism.y = y

def get_creature_population() -> list[Organism]:
    #Retrieve the list of creatures in the world
    return [
        con.WORLD_MATRIX[y][x]
        for y in range(con.DIM_Y)
        for x in range(con.DIM_X)
        if type(con.WORLD_MATRIX[y][x]) == Organism
    ]

def simulate_world():
    #Simulate the world by calculating Organism actions and executing them
    for y in range(con.DIM_Y):
        for x in range(con.DIM_X):
            if type(con.WORLD_MATRIX[y][x]) == Organism:
                con.WORLD_MATRIX[y][x].process_brain()
                con.WORLD_MATRIX[y][x].perform_actions()
    con.SIMULATION_STEP += 1

def filter_surviving_creatures():
    #Remove creatures that do not meet the survival criteria
    for y in range(con.DIM_Y):
        for x in range(con.DIM_X):
            if type(con.WORLD_MATRIX[y][x]) == Organism:
                if not con.check_survival(x, y):
                    con.WORLD_MATRIX[y][x] = 0

def breed_next_generation():
    #Generate the next generation by breeding creatures from the current population
    population = get_creature_population()
    next_gen = []
    for _ in range(con.POP_SIZE):
        parents = [
            bin(int(p.dna.replace(" ", ""), 16))[2:].zfill(
                con.LENGTH_GENE * con.LENGTH_GENOME * 4
            )
            for p in random.sample(population, k=2)
        ]
        crossover_point = random.randrange(1, con.LENGTH_GENOME * con.LENGTH_GENE * 4)

        child = parents[0][:crossover_point] + parents[1][crossover_point:]
        child = "".join(
            [
                str(int(bool(int(b)) != (random.random() < con.MUTATION_RATE)))
                for b in child
            ]
        )
        child = [
            child[i : i + con.LENGTH_GENE * 4]
            for i in range(0, con.LENGTH_GENOME * con.LENGTH_GENE * 4, con.LENGTH_GENE* 4)
        ]
        child = " ".join([hex(int(i, 2))[2:].zfill(con.LENGTH_GENOME) for i in child])

        x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)
            #print("X is "+str(x)+"Y is "+str(y))
        while con.WORLD_MATRIX[y][x] != 0:
            x, y = random.randrange(con.DIM_X), random.randrange(con.DIM_Y)

        next_gen.append(Organism(child,x,y))

    populate_creatures(next_gen)

def record_simulation_video(path: str = "videos/simulation.mp4"):
    #Record a video of the simulation and save it to the specified path
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    video = cv2.VideoWriter(path, fourcc, 30, (con.IMG_WIDTH, con.IMG_HEIGHT))

    for gen in range(con.TOTAL_GENS):
        if len(get_creature_population()) < 1:
            populate_creatures()
        elif len(get_creature_population()) > 2:
            breed_next_generation()

        for i in range(con.STEPS_PER_GEN):
            simulate_world()
            if i == 0 or i == con.STEPS_PER_GEN-1: 
                utils.render_world_snapshot(str(gen)+"_"+str(i))
            video.write(cv2.cvtColor(np.array(utils.render_world_snapshot()), cv2.COLOR_RGB2BGR))

        filter_surviving_creatures()

    print("Saving simulation video")
    video.release()
