import random
from pyvis.network import Network
import constants as params
from PIL import Image, ImageColor, ImageDraw

def create_random_dna_sequence() -> str:
   # Create a random DNA sequence
    return " ".join(
        "%06x" % random.randrange(16 ** params.LENGTH_GENE) for _ in range(params.LENGTH_GENOME)
    )

def is_within_world_limits(x_position: int, y_position: int) -> bool:
   # Verify if the given coordinates are within the world limits
    return (0 <= y_position < params.DIM_Y) and (0 <= x_position < params.DIM_X)

def render_world_snapshot(image_index=None) -> Image:
   # Render a snapshot of the current state of the world
    image = Image.new("RGB", (params.IMG_WIDTH, params.IMG_HEIGHT), (255, 255, 255))
    cell_width = params.IMG_WIDTH // params.DIM_X
    cell_height = params.IMG_HEIGHT // params.DIM_Y
    draw = ImageDraw.Draw(image)
    for y in range(params.DIM_Y):
        for x in range(params.DIM_X):
            if params.WORLD_MATRIX[y][x] != 0:
                draw.rectangle(
                    (cell_width * x, cell_height * y, cell_width * (x + 1), cell_height * (y + 1)),
                    fill=ImageColor.getcolor(params.WORLD_MATRIX[y][x].color, "RGB"),
                )

    if image_index is not None:
        image.save(f'images/world_snapshot_{image_index}.png')
    return image
