import random
import asyncio

class PyGameWeb:
    def __init__(self, canvas):
        self.canvas = canvas
        self.ctx = self.canvas.getContext('2d')
        self.keys = set()
        self.canvas.addEventListener('keydown', self._keydown)
        self.canvas.addEventListener('keyup', self._keyup)

    def _keydown(self, event):
        self.keys.add(event.code)

    def _keyup(self, event):
        self.keys.discard(event.code)

    def draw_rect(self, color, rect):
        self.ctx.fillStyle = color
        self.ctx.fillRect(*rect)

class Clock:
    def __init__(self):
        self.last_tick = None

    async def tick(self, fps):
        if self.last_tick is None:
            self.last_tick = await asyncio.sleep(0)
            return 0
        now = await asyncio.sleep(1/fps)
        dt = now - self.last_tick
        self.last_tick = now
        return dt * 1000

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Colors
BLACK = "#000000"
WHITE = "#FFFFFF"
CYAN = "#00FFFF"
YELLOW = "#FFFF00"
MAGENTA = "#FF00FF"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
ORANGE = "#FFA500"

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

COLORS = [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

def create_grid():
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid(pygame, grid):
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pygame.draw_rect(color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_tetromino(pygame, tetromino):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw_rect(tetromino.color,
                                 ((tetromino.x + x) * BLOCK_SIZE,
                                  (tetromino.y + y) * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE))

def check_collision(tetromino, grid):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                if (tetromino.x + x < 0 or tetromino.x + x >= GRID_WIDTH or
                    tetromino.y + y >= GRID_HEIGHT or
                    grid[tetromino.y + y][tetromino.x + x] != BLACK):
                    return True
    return False

def merge_tetromino(tetromino, grid):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[tetromino.y + y][tetromino.x + x] = tetromino.color

def remove_full_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]
    for row in full_rows:
        del grid[row]
        grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
    return len(full_rows)

async def main():
    grid = create_grid()
    current_piece = Tetromino()
    fall_time = 0
    fall_speed = 0.5
    score = 0
    clock = Clock()

    while True:
        fall_time += await clock.tick(60)

        keys = pygame.keys
        if "ArrowLeft" in keys:
            current_piece.move(-1, 0)
            if check_collision(current_piece, grid):
                current_piece.move(1, 0)
        elif "ArrowRight" in keys:
            current_piece.move(1, 0)
            if check_collision(current_piece, grid):
                current_piece.move(-1, 0)
        elif "ArrowDown" in keys:
            current_piece.move(0, 1)
            if check_collision(current_piece, grid):
                current_piece.move(0, -1)
        elif "ArrowUp" in keys:
            current_piece.rotate()
            if check_collision(current_piece, grid):
                for _ in range(3):
                    current_piece.rotate()

        if fall_time / 1000 > fall_speed:
            current_piece.move(0, 1)
            if check_collision(current_piece, grid):
                current_piece.move(0, -1)
                merge_tetromino(current_piece, grid)
                rows_cleared = remove_full_rows(grid)
                score += rows_cleared * 100
                current_piece = Tetromino()
                if check_collision(current_piece, grid):
                    print(f"Game Over! Score: {score}")
                    break
            fall_time = 0

        pygame.ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_grid(pygame, grid)
        draw_tetromino(pygame, current_piece)

        await asyncio.sleep(0)  # Allow other events to be processed
