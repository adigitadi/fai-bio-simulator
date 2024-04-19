from neural_node import NeuralNode
import math
import random
import constants
import utils

class SensingNode(NeuralNode):
    def compute_output(self):
        """Compute the output for the sensing node"""
        match self.identifier:
            case "POS_X_AXIS":
                # Position on the x-axis
                self.output_value = self.organism.pos_x / constants.DIM_X
            case "POS_Y_AXIS":
                # Position on the y-axis
                self.output_value = self.organism.pos_y / constants.DIM_Y
            case "CLOSEST_BOUND_X":
                # Distance to the closest boundary on the x-axis
                self.output_value = min(
                    self.organism.pos_x, constants.DIM_X - self.organism.pos_x - 1
                ) / int(constants.DIM_X / 2 - 1)
            case "CLOSEST_BOUND_X":
                # Distance to the closest boundary on the y-axis
                self.output_value = min(
                    self.organism.pos_y, constants.DIM_Y - self.organism.pos_y - 1
                ) / int(constants.DIM_Y / 2 - 1)
            case "CLOSEST_BOUND":
                # Distance to the closest boundary
                self.output_value = (
                    2
                    * min(
                        self.organism.pos_x,
                        constants.DIM_X - self.organism.pos_x - 1,
                        self.organism.pos_y,
                        constants.DIM_Y - self.organism.pos_y - 1,
                    )
                    / int(max(constants.DIM_X / 2 - 1, constants.DIM_Y / 2 - 1))
                )
            case "GENETIC_SIMILARITY_FWD":
                # Genetic similarity of the organism directly forward
                # (return 0 if no one's there)
                target_x, target_y = (
                    self.organism.pos_x + self.organism.dir_x,
                    self.organism.pos_y + self.organism.dir_y,
                )
                from organism import Organism
                if utils.is_within_world_limits(target_x, target_y) and type(constants.WORLD_MATRIX[target_y][target_x]) == Organism:
                    # Returns how many bits are different, scaled to (0, 1)
                    dna1 = "".join(
                        [
                            bin(int(gene, 16))[2:].zfill(24)
                            for gene in self.organism.dna.split(" ")
                        ]
                    )
                    dna2 = "".join(
                        [
                            bin(int(gene, 16))[2:].zfill(24)
                            for gene in constants.WORLD_MATRIX[target_y][target_x].dna.split(" ")
                        ]
                    )

                    N = 0
                    L = len(dna1)
                    for i in range(L):
                        if dna1[i] != dna2[i]:
                            N += 1
                    self.output_value = 1 - min(1, (2 * N) / L)
            case "PREV_MOVE_DIR_X":
                # Direction on the x-axis
                self.output_value = (self.organism.dir_x + 1) / 2
            case "PREV_MOVE_DIR_Y":
                # Direction on the y-axis
                self.output_value = (self.organism.dir_y + 1) / 2
            case "LONG_RANGE_POPULATION_FWD":
                # Distance to an organism in the forward direction
                for d in range(1, constants.LONG_RANGE_DIST):
                    target_x = self.organism.pos_x + d * self.organism.dir_x
                    target_y = self.organism.pos_y + d * self.organism.dir_y
                    from organism import Organism
                    if utils.is_within_world_limits(target_x, target_y) and type(constants.WORLD_MATRIX[target_y][target_x]) == Organism:
                        self.output_value = (
                            constants.LONG_RANGE_DIST - d + 1
                        ) / constants.LONG_RANGE_DIST
                        break
                self.output_value = 0
            case "LONGPROBE_BARRIER_FWD":
                # Distance to a barrier in the forward direction
                for d in range(1, constants.LONG_RANGE_DIST):
                    target_x = self.organism.pos_x + d * self.organism.dir_x
                    target_y = self.organism.pos_y + d * self.organism.dir_y
                    if utils.is_within_world_limits(target_x, target_y) and constants.WORLD_MATRIX[target_y][target_x] == "B":
                        self.output_value = (
                            constants.LONG_RANGE_DIST - d + 1
                        ) / constants.LONG_RANGE_DIST
                        break
                self.output_value = 0
            case "POP_DENSITY":
                # Population density in surrounding area
                count = 0
                for delta_x in range(
                    -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                ):
                    for delta_y in range(
                        -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                    ):
                        if delta_x == 0 and delta_y == 0:
                            continue
                        target_x = self.organism.pos_x + delta_x
                        target_y = self.organism.pos_y + delta_y
                        from organism import Organism
                        if (
                            utils.is_within_world_limits(target_x, target_y)
                            and type(constants.WORLD_MATRIX[target_y][target_x]) == Organism
                        ):
                            count += 1
                self.output_value = count / ((constants.SENSOR_RADIUS_POP * 2 + 1) ** 2 - 1)
            case "POP_DENSITY_FWD":
                count = 0
                for delta_x in range(
                    -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                ):
                    for delta_y in range(
                        -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                    ):
                        if delta_x == 0 and delta_y == 0:
                            continue
                        target_x = self.organism.pos_x + delta_x
                        target_y = self.organism.pos_y + delta_y
                        from organism import Organism
                        if (
                            utils.is_within_world_limits(target_x, target_y)
                            and type(constants.WORLD_MATRIX[target_y][target_x]) == Organism
                        ):
                            count += (
                                self.organism.dir_x * delta_x
                                + self.organism.dir_y * delta_y
                            ) / (delta_x * delta_x + delta_y * delta_y)
                max_sum = 3 * (2 * constants.SENSOR_RADIUS_POP + 1)
                assert count >= -max_sum and count <= max_sum
                self.output_value = (count / max_sum + 1) / 2
            case "POP_DENSITY_LR":
                # Similar to the POPULATION_FWD neuron, but for left-right direction
                count = 0
                for delta_x in range(
                    -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                ):
                    for delta_y in range(
                        -constants.SENSOR_RADIUS_POP, constants.SENSOR_RADIUS_POP + 1
                    ):
                        if delta_x == 0 and delta_y == 0:
                            continue
                        target_x = -self.organism.dir_y + delta_x
                        target_y = self.organism.dir_x + delta_y
                        from organism import Organism
                        if (
                            utils.is_within_world_limits(target_x, target_y)
                            and type(constants.WORLD_MATRIX[target_y][target_x]) == Organism
                        ):
                            count += (
                                -self.organism.dir_y * delta_x
                                + self.organism.dir_x * delta_y
                            ) / (delta_x * delta_x + delta_y * delta_y)
                max_sum = 3 * (2 * constants.SENSOR_RADIUS_POP + 1)
                assert count >= -max_sum and count <= max_sum
                self.output_value = (count / max_sum + 1) / 2
            case "OSCILLATOR":
                # Output of a cos function with phase determined by organism's age
                phase = (constants.SIMULATION_STEP % self.organism.oscillator_period) / self.organism.oscillator_period
                self.output_value = (math.cos(phase * 2 * math.pi) + 1) / 2
                self.output_value = (
                    1 if self.output_value > 1 else (0 if self.output_value < 0 else self.output_value)
                )
            case "AGE":
                # Age of the organism, which is the same as age of the world
                self.output_value = constants.SIMULATION_STEP / constants.STEPS_PER_GEN
            case "BARRIER_FWD":
                # How far away a barrier is in the forward direction
                self.output_value = self.calculate_sensor_range(
                    self.organism.dir_x, self.organism.dir_y
                )
            case "BARRIER_LR":
                # How far away a barrier is in the left-right direction
                self.output_value = self.calculate_sensor_range(
                    -self.organism.dir_y, self.organism.dir_x
                )
            case "RANDOM":
                # random float in (0, 1), uniform
                self.output_value = random.random()
            case _:
                raise TypeError(f"Invalid sensory neuron {self.identifier}")

    def calculate_sensor_range(self, x_axis: int, y_axis: int):
        count_fwd = 0
        count_rev = 0
        num_locs_to_test = constants.SHORT_PROBE_DIST

        tx, ty = self.organism.pos_x + x_axis, self.organism.pos_y + y_axis
        while (
            num_locs_to_test > 0 and utils.is_within_world_limits(tx, ty) and constants.WORLD_MATRIX[ty][tx] != "B"
        ):
            count_fwd += 1
            tx += x_axis
            ty += y_axis
            num_locs_to_test -= 1
        if num_locs_to_test > 0 and not utils.is_within_world_limits(tx, ty):
            count_fwd = num_locs_to_test

        num_locs_to_test = constants.SHORT_PROBE_DIST
        tx, ty = self.organism.pos_x - x_axis, self.organism.pos_y - y_axis
        while (
            num_locs_to_test > 0 and utils.is_within_world_limits(tx, ty) and constants.WORLD_MATRIX[ty][tx] != "B"
        ):
            count_rev += 1
            tx -= x_axis
            ty -= y_axis
            num_locs_to_test -= 1
        if num_locs_to_test > 0 and not utils.is_within_world_limits(tx, ty):
            count_rev = num_locs_to_test
        return (count_fwd - count_rev + constants.SHORT_PROBE_DIST) / (
            2 * constants.SHORT_PROBE_DIST
        )
