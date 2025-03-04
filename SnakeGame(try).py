"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random


# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 440

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

# Colors (R, G, B)
BLACK = pygame.Color(51, 51, 51)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(204, 51, 0)
GREEN = pygame.Color(204, 255, 153)
BLUE = pygame.Color(0, 51, 102)

# GAME STATE CLASS
class GameState:
    def __init__(self, FRAME_SIZE):
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0]//10)) * 10, random.randrange(1, (FRAME_SIZE[1]//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        self.outcome = "continue"

# Game Over
def game_over(game):
    print_line_data(game)
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, WHITE)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLUE)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(game, 0, WHITE, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

# Score
def show_score(game, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(game.score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (FRAME_SIZE_X/8, 15)
    else:
        score_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

# Move the snake
def move_keyboard(game, event):
    # Whenever a key is pressed down
    change_to = game.direction
    if event.type == pygame.KEYDOWN:
        # W -> Up; S -> Down; A -> Left; D -> Right
        if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
            change_to = 'UP'
        if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
            change_to = 'DOWN'
        if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
            change_to = 'LEFT'
        if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
            change_to = 'RIGHT'
    return change_to

def get_safe_moves(game):

    left_safe  = False
    right_safe = False
    up_safe    = False
    down_safe  = False

    if game.direction != 'RIGHT':
        left_safe  = (game.snake_pos[0] - 10 >= 0) and ([game.snake_pos[0] - 10, game.snake_pos[1]] not in game.snake_body)
    if game.direction != 'LEFT':
        right_safe = (game.snake_pos[0] + 10 < FRAME_SIZE_X) and ([game.snake_pos[0] + 10, game.snake_pos[1]] not in game.snake_body)
    if game.direction != 'DOWN':
        up_safe    = (game.snake_pos[1] - 10 >= 0) and ([game.snake_pos[0], game.snake_pos[1] - 10] not in game.snake_body)
    if game.direction != 'UP':
        down_safe  = (game.snake_pos[1] + 10 < FRAME_SIZE_Y) and ([game.snake_pos[0], game.snake_pos[1] + 10] not in game.snake_body)

    return {
        "LEFT": left_safe,
        "RIGHT": right_safe,
        "UP": up_safe,
        "DOWN": down_safe
    }


from collections import deque


def simulate_move(pos, direction):
    # Returns the new head position if a move is made in the given direction.
    x, y = pos
    if direction == 'UP':
        return (x, y - 10)
    if direction == 'DOWN':
        return (x, y + 10)
    if direction == 'LEFT':
        return (x - 10, y)
    if direction == 'RIGHT':
        return (x + 10, y)
    return pos


def flood_fill_count(game, start):
    # Counts how many free cells are reachable from start, treating snake_body as obstacles.
    grid_w = FRAME_SIZE_X
    grid_h = FRAME_SIZE_Y
    cell_size = 10
    visited = set()
    queue = deque([start])
    # Create a set for fast lookup of snake body cells.
    snake_set = set(tuple(x) for x in game.snake_body)
    count = 0
    while queue:
        pos = queue.popleft()
        if pos in visited:
            continue
        visited.add(pos)
        count += 1
        for dx, dy in [(10, 0), (-10, 0), (0, 10), (0, -10)]:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if (0 <= new_pos[0] < grid_w and 0 <= new_pos[1] < grid_h and
                    new_pos not in snake_set and new_pos not in visited):
                queue.append(new_pos)
    return count


def move_tutorial_1(game):
    """
    Improved AI: For every safe move from the current head position,
    simulate the next move and count how many grid cells are reachable using flood-fill.
    Then choose the move that maximizes the free area.
    In case of a tie, choose the one that minimizes the Manhattan distance to the food.
    """
    safe_moves = get_safe_moves(game)
    current_head = tuple(game.snake_pos)

    candidates = []
    for direction, is_safe in safe_moves.items():
        if is_safe:
            new_head = simulate_move(current_head, direction)
            # Evaluate available free area after this move.
            area = flood_fill_count(game, new_head)
            # Manhattan distance to food (smaller is better)
            food_distance = abs(game.food_pos[0] - new_head[0]) + abs(game.food_pos[1] - new_head[1])
            candidates.append((direction, area, food_distance))

    # If no safe move is available, fall back (this will trigger game over soon).
    if not candidates:
        return game.direction

    # Choose the move with the largest flood fill area.
    # In case of ties, choose the one that minimizes distance to the food.
    candidates.sort(key=lambda item: (item[1], -item[2]), reverse=True)
    best_move = candidates[0][0]
    return best_move


# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def print_line_data(game):
    # Define the filename
    filename = "snake_game_log.arff"

    header = """@RELATION snake_game

@ATTRIBUTE snake_pos_x NUMERIC
@ATTRIBUTE snake_pos_y NUMERIC
@ATTRIBUTE snake_body_length NUMERIC
@ATTRIBUTE food_pos_x NUMERIC
@ATTRIBUTE food_pos_y NUMERIC
@ATTRIBUTE horizontal_distance NUMERIC
@ATTRIBUTE vertical_distance NUMERIC
@ATTRIBUTE score NUMERIC
@ATTRIBUTE body_parts NUMERIC
@ATTRIBUTE left_safe {True, False}
@ATTRIBUTE right_safe {True, False}
@ATTRIBUTE up_safe {True, False}
@ATTRIBUTE down_safe {True, False}
@ATTRIBUTE fully_safe_LEFT {True, False}
@ATTRIBUTE fully_safe_RIGHT {True, False}
@ATTRIBUTE fully_safe_UP {True, False}
@ATTRIBUTE fully_safe_DOWN {True, False}
@ATTRIBUTE New_direction {LEFT, RIGHT, UP, DOWN}


@DATA
"""

    # Check if the file exists, if not, write the header
    try:
        with open(filename, "r") as file:
            pass
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write(header)

    # Calculate distances to food
    horizontal_distance = game.food_pos[0] - game.snake_pos[0]
    vertical_distance = game.food_pos[1] - game.snake_pos[1]

    # Safe moves for x, y directions
    safe_moves = get_safe_moves(game)

    # Amount of body parts
    body_parts = len(game.snake_body)


    # Data to log
    data_line = (
        f"{game.snake_pos[0]},{game.snake_pos[1]},{len(game.snake_body)},"
        f"{game.food_pos[0]},{game.food_pos[1]},{horizontal_distance},{vertical_distance},{game.score},"
        f"{body_parts},{safe_moves['LEFT']},{safe_moves['RIGHT']},{safe_moves['UP']},{safe_moves['DOWN']},"
        f"\"{game.direction}\"\n"
    )

    # Append data to the file
    with open(filename, "a") as file:
        file.write(data_line)

# Checks for errors encounteRED
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialise game window
pygame.display.set_caption('Snake Eater - Machine Learning (UC3M)')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Main logic
game = GameState((FRAME_SIZE_X,FRAME_SIZE_Y))
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        # CALLING MOVE METHOD
        #game.direction = move_keyboard(game, event)

    # UNCOMMENT WHEN METHOD IS IMPLEMENTED
    game.direction = move_tutorial_1(game)

    # Save Current State
    print_line_data(game)


    # Moving the snake
    if game.direction == 'UP':
        game.snake_pos[1] -= 10
    if game.direction == 'DOWN':
        game.snake_pos[1] += 10
    if game.direction == 'LEFT':
        game.snake_pos[0] -= 10
    if game.direction == 'RIGHT':
        game.snake_pos[0] += 10

    # Snake body growing mechanism
    game.snake_body.insert(0, list(game.snake_pos))
    if game.snake_pos[0] == game.food_pos[0] and game.snake_pos[1] == game.food_pos[1]:
        game.score += 100
        game.food_spawn = False
    else:
        game.snake_body.pop()
        game.score -= 1

    # Spawning food on the screen
    if not game.food_spawn:
        game.food_pos = [random.randrange(1, (FRAME_SIZE_X//10)) * 10, random.randrange(1, (FRAME_SIZE_Y//10)) * 10]
    game.food_spawn = True

    # GFX
    game_window.fill(BLUE)
    for pos in game.snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    # Snake food
    pygame.draw.rect(game_window, RED, pygame.Rect(game.food_pos[0], game.food_pos[1], 10, 10))

    # Game Over conditions
    # Getting out of bounds
    if game.snake_pos[0] < 0 or game.snake_pos[0] > FRAME_SIZE_X-10:
        game.outcome = "gameover"
        game_over(game)
    if game.snake_pos[1] < 0 or game.snake_pos[1] > FRAME_SIZE_Y-10:
        game.outcome = "gameover"
        game_over(game)
    # Touching the snake body
    for block in game.snake_body[1:]:
        if game.snake_pos[0] == block[0] and game.snake_pos[1] == block[1]:
            game.outcome = "gameover"
            game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(DIFFICULTY)
    # PRINTING STATE
    print_state(game)


