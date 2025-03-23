"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random
from wekaI import Weka

# Initialize the Weka instance
weka = Weka()
weka.start_jvm()


# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 10

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
    weka.stop_jvm()
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


def future_score(game):

    predicted_score = game.score

    next_pos = game.snake_pos[:]
    if game.direction == 'UP':
        next_pos[1] -= 10
    elif game.direction == 'DOWN':
        next_pos[1] += 10
    elif game.direction == 'LEFT':
        next_pos[0] -= 10
    elif game.direction == 'RIGHT':
        next_pos[0] += 10

    if next_pos == game.food_pos:
        predicted_score += 100
    else:
        predicted_score -= 1
    return predicted_score



# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def move_tutorial_1(game):
    change_to = game.direction
    safe_moves = get_safe_moves(game)
    horizontal_distance = game.food_pos[0] - game.snake_pos[0]
    vertical_distance = game.food_pos[1] - game.snake_pos[1]

    # Move vertically first because of spawn movement direction of snake
    if vertical_distance > 0 and safe_moves["DOWN"]:
        change_to = "DOWN"
    elif vertical_distance < 0 and safe_moves["UP"]:
        change_to = "UP"
    elif horizontal_distance > 0 and safe_moves["RIGHT"]:
        change_to = "RIGHT"
    elif horizontal_distance < 0 and safe_moves["LEFT"]:
        change_to = "LEFT"

    # If the chosen move is blocked, look for the safest alternative
    if not safe_moves[change_to]:
        possible_moves = [d for d in ["LEFT", "RIGHT", "UP", "DOWN"] if safe_moves[d]]
        if possible_moves:
            change_to = possible_moves[0]  # Pick any safe move

    return change_to


# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)


def get_body_distances(game):
    head_x, head_y = game.snake_pos
    left_dist = right_dist = up_dist = down_dist = FRAME_SIZE_X  # Default max value

    for segment in game.snake_body[1:]:
        seg_x, seg_y = segment

        if seg_y == head_y and seg_x < head_x:  # Left
            left_dist = min(left_dist, head_x - seg_x)
        elif seg_y == head_y and seg_x > head_x:  # Right
            right_dist = min(right_dist, seg_x - head_x)
        elif seg_x == head_x and seg_y < head_y:  # Up
            up_dist = min(up_dist, head_y - seg_y)
        elif seg_x == head_x and seg_y > head_y:  # Down
            down_dist = min(down_dist, seg_y - head_y)

    return left_dist, right_dist, up_dist, down_dist


def move_weka_agent(game, weka):
    x = [
        game.snake_pos[0], game.snake_pos[1], len(game.snake_body),  # Numerical
        game.food_pos[0], game.food_pos[1], game.food_pos[0] - game.snake_pos[0],  # Numerical
                                            game.food_pos[1] - game.snake_pos[1], game.score, len(game.snake_body),
        # Numerical
        int(get_safe_moves(game)["LEFT"]),
        int(get_safe_moves(game)["RIGHT"]),
        int(get_safe_moves(game)["UP"]),
        int(get_safe_moves(game)["DOWN"]),
        get_body_distances(game)[0], get_body_distances(game)[1],  # Numerical
        get_body_distances(game)[2], get_body_distances(game)[3],  # Numerical
        future_score(game)  # Numerical
    ]

    model_path = "j48.model"
    dataset_path = "snake_game_log_data_training1.arff"

    predicted_action = weka.predict(model_path, x, dataset_path)

    action_map = {0: "LEFT", 1: "RIGHT", 2: "UP", 3: "DOWN"}
    return action_map.get(predicted_action, game.direction)


def print_line_data(game):
    filename = "snake_game_log2.arff"

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
@ATTRIBUTE left_safe NUMERIC
@ATTRIBUTE right_safe NUMERIC
@ATTRIBUTE up_safe NUMERIC
@ATTRIBUTE down_safe NUMERIC
@ATTRIBUTE left_distance NUMERIC
@ATTRIBUTE right_distance NUMERIC
@ATTRIBUTE up_distance NUMERIC
@ATTRIBUTE down_distance NUMERIC
@ATTRIBUTE New_direction NUMERIC
@ATTRIBUTE future_score NUMERIC

@DATA
"""

    try:
        with open(filename, "r") as file:
            pass
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write(header)

    horizontal_distance = game.food_pos[0] - game.snake_pos[0]
    vertical_distance = game.food_pos[1] - game.snake_pos[1]
    safe_moves = get_safe_moves(game)
    body_parts = len(game.snake_body)
    left_dist, right_dist, up_dist, down_dist = get_body_distances(game)

    next_score = 0 if game.outcome == "gameover" else future_score(game)

    direction_encoding = {"LEFT": 0, "RIGHT": 1, "UP": 2, "DOWN": 3}
    direction_numeric = direction_encoding.get(game.direction, -1)

    data_line = (
        f"{game.snake_pos[0]},{game.snake_pos[1]},{len(game.snake_body)},"
        f"{game.food_pos[0]},{game.food_pos[1]},{horizontal_distance},{vertical_distance},{game.score},"
        f"{body_parts},{int(safe_moves['LEFT'])},{int(safe_moves['RIGHT'])},{int(safe_moves['UP'])},{int(safe_moves['DOWN'])},"
        f"{left_dist},{right_dist},{up_dist},{down_dist},"
        f"{direction_numeric},{next_score}\n"
    )

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
    #game.direction = move_tutorial_1(game)
    #WEKA AGENTE
    game.direction = move_weka_agent(game, weka)

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


