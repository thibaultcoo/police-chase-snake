# library initialization
import pygame
import random
import sys
import numpy as np
import scipy.stats as stats
from datetime import datetime, timedelta

# game initialization
pygame.init()
pygame.display.set_caption('Enhanced Snake Game')

# colors initialization
black = (0, 0, 0)
grey = (50, 50, 50)
white = (255, 255, 255)
red = (180, 70, 80)
dark_red = (139, 0, 0)
green = (0, 255, 0)
blue = (50, 153, 213)
dark_green = (0, 125, 0)
dark_blue = (0, 0, 139)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
bright_blue = (0, 0, 255)

# moves initialization
down = pygame.K_DOWN
up = pygame.K_UP
left = pygame.K_LEFT
right = pygame.K_RIGHT
anykey = pygame.KEYDOWN
stop = pygame.QUIT
q = pygame.K_q
c = pygame.K_c
key2 = pygame.K_KP2
key4 = pygame.K_KP4
key6 = pygame.K_KP6
key8 = pygame.K_KP8

# food types initialization
foodDicts = {'regular': bright_blue, 'double': bright_red, 'fast': green}
secondsMultiplier = 5
fasterMultiplier = 2

# obstacles grid initialization (depending on difficulty)
init_grid_format = {"easy": 3, "medium": 5, "hard": 5}
speed = {"easy": 10, "medium": 17, "hard": 25}

# display initialization
dis_width = 1000
dis_height = 720
snake_block = 10
dis = pygame.display.set_mode((dis_width, dis_height))
font_style = pygame.font.SysFont("bahnschrift", 25)
clock = pygame.time.Clock()

# additional variables related to the police chase feature
inside_circle_radius = 10 # largest circle inside a square
outside_circle_radius = np.sqrt(200) # smallest circle outside a squre
police_turbo = 1.10

# non-crossable borders initialization (will be filled with tuples of coordinates)
borders = []

class pattern():
    """
    class responsible for interacting with the obstacle objects
    the pattern created is randomly generated and its complexity is positively correlated with the difficulty
    several points are first generated to form a grid - those points will be the center of future obstacle objects
    each object is then attributed random dimensions, all of which is finally displayed on the screen
    each point of coordinates of the pattern is saved in a list, in an effort to generalize its non-crossable property
    """

    def __init__(self, difficulty, dis_width, dis_height, snake_block):
        self.color = grey
        self.difficulty = difficulty
        self.dis_width = dis_width
        self.dis_height = dis_height
        self.snake_block = snake_block

    def build_grid(self):
        """
        as mentionned above, following a grid format depending on difficulty, 
        random coordinates are generated and stored within x_coord and y_coord
        """

        grid = []
        grid_format = init_grid_format[self.difficulty]
        
        for x_case in range (grid_format):
            for y_case in range(grid_format):
                if (x_case, y_case) != (int((grid_format)/2), int((grid_format)/2)): 
                    x_coord = random.randint(int(self.dis_width / grid_format * x_case), int(self.dis_width / grid_format * (1 + x_case)))
                    y_coord = random.randint(int(self.dis_height / grid_format * y_case), int(self.dis_height / grid_format * (1 + y_case)))
                    grid.append([x_coord, y_coord])

        return grid
    
    def build_rectangle(self, x_coord, y_coord, obstacle_height, obstacle_width):
        for x in range(x_coord - obstacle_width, x_coord + obstacle_width + 1):
            for y in range(y_coord - obstacle_height, y_coord + obstacle_height + 1):
                borders.append([x, y])

    def build_diamond(self, x_coord, y_coord, obstacle_height):
        if obstacle_height % 2 == 0: obstacle_height += 1

        for x in range(x_coord - obstacle_height, x_coord + obstacle_height + 1):
            for y in range(y_coord - obstacle_height + abs(x - x_coord), y_coord + obstacle_height - abs(x - x_coord)):
                borders.append([x, y])
    
    def block_coordinates(self):
        value = stats.norm.cdf(np.random.normal())

        if self.difficulty == "easy": return int(15 + 10 * value)
        if self.difficulty == "medium": return int(20 + 14 * value)
        if self.difficulty == "hard": return int(25 + 18 * value)

    def build_block(self, x_coord, y_coord):
        """
        based on the grid of points generated above
        this function will generate random-sized forms around each point
        """

        if self.difficulty != "hard": form = "rectangle" 
        else: form = random.choice(["rectangle", "diamond"])

        # random block dimensions generator
        obstacle_height = self.block_coordinates()
        obstacle_width = self.block_coordinates()

        if form == "rectangle": self.build_rectangle(x_coord, y_coord, obstacle_height, obstacle_width)
        if form == "diamond": self.build_diamond(x_coord, y_coord, obstacle_height)

    def build_pattern(self):
        self.destroy_pattern()

        grid = self.build_grid()
        for ele in grid: self.build_block(ele[0], ele[1])

    def print_pattern(self, x_coord, y_coord):
        pygame.draw.rect(dis, self.color, [x_coord, y_coord, self.snake_block, self.snake_block])

    def destroy_pattern(self):
        borders.clear()

class food():
    """
    class responsible for interacting with the food object
    generates food position depending on where the obstacles are
    handles different types of food and their specifics
    """

    def __init__(self, snake_speed):
        self.x_coord = None
        self.y_coord = None
        self.food_type = None
        self.snake_speed = snake_speed

    def generate(self):
        self.x_coord = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
        self.y_coord = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
        if [self.x_coord + 1.5 * snake_block, self.y_coord + 1.5 * snake_block] in borders: self.generate()
        if [self.x_coord - 1.5 * snake_block, self.y_coord + 1.5 * snake_block] in borders: self.generate()
        if [self.x_coord + 1.5 * snake_block, self.y_coord - 1.5 * snake_block] in borders: self.generate()
        if [self.x_coord - 1.5 * snake_block, self.y_coord - 1.5 * snake_block] in borders: self.generate()

        self.foodtype = np.random.choice(list(foodDicts.keys()), 1, p=[0.6, 0.3, 0.1])[0]

    def handle_accelerators(self, accelerator):
        if datetime.now() > accelerator[0]:
            accelerator.pop(0)
            self.snake_speed /= fasterMultiplier

class snake():
    """
    class responsible for interacting with the snake object
    controls its position and moves at every frame, depending on the potential action of the user
    encompasses multiple tests of illegal positions (snake touching its tail, snake touching obstacles)
    as well as legal positions (snake eating food or snake going through the screen)
    """

    def __init__(self, x_coord, y_coord, x_shift, y_shift, length, surface, accelerator):
        self.color = dark_green
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.length = length
        self.surface = surface
        self.accelerator = accelerator

    def move_up(self, boost=1):
        self.y_shift = -boost * snake_block
        self.x_shift = 0

    def move_down(self, boost=1):
        self.y_shift = boost * snake_block
        self.x_shift = 0

    def move_left(self, boost=1):
        self.x_shift = -boost * snake_block
        self.y_shift = 0

    def move_right(self, boost=1):
        self.x_shift = boost * snake_block
        self.y_shift = 0

    def position_update(self):
        self.x_coord += self.x_shift
        self.y_coord += self.y_shift

    def is_hitting_himself(self):
        if [self.x_coord, self.y_coord] in self.surface[:-1]: return True

    def is_hitting_obstacle(self):
        """
        we check if any of the four corners of the snake's head in touching an obstacle
        to that end we verify that none of those points are inside the list of coordinates deemed as obstacles
        """

        if [self.x_coord + snake_block, self.y_coord] in borders: return True
        if [self.x_coord - snake_block, self.y_coord] in borders: return True
        if [self.x_coord, self.y_coord + snake_block] in borders: return True
        if [self.x_coord, self.y_coord - snake_block] in borders: return True

    def is_breaching(self):
        if self.x_coord >= dis_width:
            self.x_coord = 0
            left
        elif self.x_coord < 0:
            self.x_coord = dis_width
            right
        if self.y_coord >= dis_height:
            self.y_coord = 0
            up
        elif self.y_coord < 0:
            self.y_coord = dis_height
            down

    def ate_food(self, type_food):
        if type_food == "double": self.length += 2 
        else: self.length += 1

        if type_food == "fast":
            self.accelerator.append(datetime.now() + timedelta(seconds=secondsMultiplier))

    def builder(self):
        self.surface.append([self.x_coord, self.y_coord])
        if len(self.surface) > self.length: del self.surface[0]

        self.move()

    def move(self):
        for x in self.surface:
            pygame.draw.rect(dis, self.color, [x[0], x[1], snake_block, snake_block])
 
class police(snake):
    """
    class responsible for interacting with the police object that chases the snake
    because its structure resembles a lot the snake, we decided to apply inheritancy here
    handles its movements depending on the position of the snake, as well as some tests for illegal positions
    at each frame the future position is decided by an algorithm that computes the move that minimizes the distance
    to the snake (80% best move and 20% random move), while checking if that move is legal, ie not within an obstacle
    """

    def __init__(self):
        super().__init__
        self.x_coord = None
        self.y_coord = None
        self.x_shift = 0
        self.y_shift = 0
        self.x_snake = 0
        self.y_snake = 0     
        self.color = dark_blue
        self.surface = []
        self.length = 1

    def set_coordinates(self):
        """
        we set initial coordinates for the police object here
        and we ensure that the set of coordinates generated is legal, ie it does not touch any obstacle
        """

        self.x_coord = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
        self.y_coord = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
        if [self.x_coord + snake_block, self.y_coord] in borders: self.set_coordinates()
        if [self.x_coord - snake_block, self.y_coord] in borders: self.set_coordinates()
        if [self.x_coord, self.y_coord + snake_block] in borders: self.set_coordinates()
        if [self.x_coord, self.y_coord - snake_block] in borders: self.set_coordinates()

    def position_update(self):
        super().position_update()

    def hyp_distance_from_snake(self, hyp_coord):
        return np.sqrt((hyp_coord[0] - self.x_snake)**2 + (hyp_coord[1] - self.y_snake)**2)

    def best_move(self):
        """
        this function will compute each of the four theoretical moves (up, down, left or right)
        and calculate what would the new distance to the snake be
        as the goal of the cop is to capture the snake, we search for the move that minimizes that distance
        """

        coord_if_move_up = [self.x_coord, self.y_coord - snake_block]
        coord_if_move_down = [self.x_coord, self.y_coord + snake_block]
        coord_if_move_left = [self.x_coord - snake_block, self.y_coord]
        coord_if_move_right = [self.x_coord + snake_block, self.y_coord]

        dis_if_move_up = self.hyp_distance_from_snake(hyp_coord=coord_if_move_up)
        dis_if_move_down = self.hyp_distance_from_snake(hyp_coord=coord_if_move_down)
        dis_if_move_left = self.hyp_distance_from_snake(hyp_coord=coord_if_move_left)
        dis_if_move_right = self.hyp_distance_from_snake(hyp_coord=coord_if_move_right)

        min_distance = min(dis_if_move_up, dis_if_move_down, dis_if_move_left, dis_if_move_right)
        if min_distance == dis_if_move_up: self.move_up()
        if min_distance == dis_if_move_down: self.move_down()
        if min_distance == dis_if_move_left: self.move_left()
        if min_distance == dis_if_move_right: self.move_right()

    def random_move(self):
        """
        we want our cop not to be perfect in finding us, otherwise we think it would be too hard for the snake to escape
        so we account for a probability of a random cop move
        """

        choice = np.random.choice(["up", "down", "right", "left", "nothing"], 1, [0.05, 0.05, 0.05, 0.05, 0.8])[0]
        if choice == "up": self.move_up()
        elif choice == "down": self.move_down()
        elif choice == "right": self.move_right()
        elif choice == "left": self.move_left()

    def builder(self, x_snake, y_snake):
        self.x_snake = x_snake
        self.y_snake = y_snake

        self.direction_algorithm()
        super().builder()

    def direction_algorithm(self):
        """
        at each frame we let the cop decide on where to move, assuming he is not brilliant every time
        we also account for the legality of the move, by canceling the shifts and re-running the function if the move
        was deemed to breach an obstacle
        once the theoretical move is accepted, the police position is updated for the user to see
        """

        best_move = np.random.choice([False, True], 1, [0.2, 0.8])[0]

        if best_move: self.best_move()
        else: self.random_move()

        if self.is_close_to_obstacles():
            self.x_shift = 0
            self.y_shift = 0
            self.position_update()
            self.direction_algorithm()

        else: self.position_update()

    def blinking(self):
        if self.color == dark_blue: self.color = dark_red
        else: self.color = dark_blue

        return datetime.now()

    def is_breaching(self):
        super().is_breaching()

    def is_close_to_obstacles(self):
        temp_x = self.x_coord + self.x_shift
        temp_y = self.y_coord + self.y_shift
        
        if [temp_x, temp_y] in borders: return True
        if [temp_x + snake_block, temp_y + snake_block] in borders: return True
        if [temp_x - snake_block, temp_y + snake_block] in borders: return True
        if [temp_x + snake_block, temp_y - snake_block] in borders: return True
        if [temp_x - snake_block, temp_y - snake_block] in borders: return True

    def move_down(self):
        super().move_down(boost=police_turbo)

    def move_up(self):
        super().move_up(boost=police_turbo)

    def move_left(self):
        super().move_left(boost=police_turbo)

    def move_right(self):
        super().move_right(boost=police_turbo)

    def is_hitting_snake(self, snake_surface):
        """
        the capture detection algorithm forces us to use a circle hitbox for each of the snake squares, for simplicity
        using a mix of inner and outer circle from each square of the snake surface
        we calculate the distance from each corner of the cop to each center of the snake surface's squares
        if one of those results is below the radius, it means that the cop is partially inside the snake's hitbox
        and therefore the cop captured us
        """

        snake_hitbox_radius = 0.8 * inside_circle_radius + 0.2 * outside_circle_radius
        for blocks in snake_surface:
            if np.sqrt(((self.x_coord - snake_block) - blocks[0])**2 + ((self.y_coord - snake_block) - blocks[1])**2) < snake_hitbox_radius: return True
            if np.sqrt(((self.x_coord + snake_block) - blocks[0])**2 + ((self.y_coord - snake_block) - blocks[1])**2) < snake_hitbox_radius: return True
            if np.sqrt(((self.x_coord - snake_block) - blocks[0])**2 + ((self.y_coord + snake_block) - blocks[1])**2) < snake_hitbox_radius: return True
            if np.sqrt(((self.x_coord + snake_block) - blocks[0])**2 + ((self.y_coord + snake_block) - blocks[1])**2) < snake_hitbox_radius: return True

def game_loop(difficulty, police_chase=False):
    """
    main game function, will run the game based on the selected difficulty and user action
    handles the direction of the snake based on what key is pressed (if any is) as well as the snake actions/constraints
    comments are written along the way when judged necessary, so as to clearly grasp how the code is structured
    """

    # initializes some game management parameters
    game_over = game_close = key_pressed = False
    last_blink = datetime.now()

    # initializes the game
    snake_speed = speed[difficulty]
    dis.fill(black)

    # initializes the snake position
    x_coord = dis_width / 2
    y_coord = dis_height / 2

    # initializes our snake object
    our_snake = snake(x_coord=x_coord, y_coord=y_coord, x_shift=0, y_shift=0, length=1, surface=[], accelerator=[])

    # builds our obstacles pattern at inception
    our_obstacles = pattern(difficulty=difficulty, dis_width=dis_width, dis_height=dis_height, snake_block=snake_block)
    our_obstacles.build_pattern()

    # initializes our police object
    if police_chase: our_police = police()

    # we print the pattern at last and save it (so as to copy paste it at each future frame)
    for coord in borders: our_obstacles.print_pattern(coord[0], coord[1])
    saved_surface = pygame.Surface((dis_width, dis_height))
    saved_surface.blit(dis, (0, 0))

    # initializes our food object and generates the first one
    our_food = food(snake_speed=snake_speed)
    our_food.generate()

    # places out our police object
    if police_chase: our_police.set_coordinates()

    # while the game is not lost this loop is entered
    while not game_over:

        # if the game is lost we check if we want to close it or not
        while game_close == True: 
            close_game(our_snake.length)
            for event in pygame.event.get():
                if event.type == anykey:
                    if event.key == q:
                        game_over = True
                        game_close = False
                    if event.key == c: main_menu()

        # we move our snake following the user input (if any)
        for event in pygame.event.get():
            if event.type == stop: game_over = True

            if event.type == anykey:
                key_pressed = True

                if event.key == left: our_snake.move_left()
                elif event.key == right: our_snake.move_right()
                elif event.key == up: our_snake.move_up()
                elif event.key == down: our_snake.move_down()

        # we update the position of our snake and copy the obstacles background
        our_snake.position_update()
        dis.blit(saved_surface, (0, 0))

        # we display the food
        pygame.draw.rect(dis, foodDicts[our_food.foodtype], [our_food.x_coord, our_food.y_coord, snake_block, snake_block])

        # fast multiplier handler (if a speed multiplier food has been eaten)
        if len(our_snake.accelerator) > 0: our_food.handle_accelerators(our_snake.accelerator)

        # builds the snake from the user input (as well as the cop if the game mode is selected)
        our_snake.builder()
        if police_chase and key_pressed: our_police.builder(x_snake=our_snake.x_coord, y_snake=our_snake.y_coord)

        # checks if the cop captured the snake
        if police_chase and our_police.is_hitting_snake(snake_surface=our_snake.surface): game_close = True

        # handling the ability to go the opposite side when hitting the wall
        our_snake.is_breaching()
        if police_chase: our_police.is_breaching()

        # handles illegal wall touches
        if our_snake.is_hitting_obstacle(): game_close = True

        # handles touching its tail
        if our_snake.is_hitting_himself(): game_close = True

        # updates the score continuously
        scoring_update(our_snake.length - 1)

        # blinking police light
        if police_chase and last_blink + timedelta(seconds=0.2) < datetime.now(): last_blink = our_police.blinking()

        pygame.display.update()

        # eaten food handler
        if our_snake.x_coord == our_food.x_coord and our_snake.y_coord == our_food.y_coord:      
            our_snake.ate_food(our_food.foodtype)
            if our_food.foodtype == 'fast': our_food.snake_speed *= fasterMultiplier

            # if the food is eaten, we generate a new one
            our_food = food(snake_speed=our_food.snake_speed)
            our_food.generate()

        clock.tick(our_food.snake_speed)

    pygame.quit()
    quit()

# creates the buttons
def draw_button(button_text, x, y, w, h, inactive_color, active_color, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # if the mouse is hovering the box
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(dis, active_color, (x, y, w, h))

        # if the mouse is clicking the box
        if click[0] == 1 and action is not None:
            action()         
    else:
        pygame.draw.rect(dis, inactive_color, (x, y, w, h))

    text_surf = font_style.render(button_text, True, black)
    text_rect = text_surf.get_rect()
    text_rect.center = ((x+(w/2)), (y+(h/2)))
    dis.blit(text_surf, text_rect)

# displays the score
def scoring_update(score):
    value = font_style.render("Your Score: " + str(score), True, white)
    dis.blit(value, [0, 0])

# displays messages
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 3, dis_height / 2])

# easy difficulty setter
def set_easy():
    game_loop(difficulty='easy')

# medium difficulty setter
def set_medium():
    game_loop(difficulty='medium')

# hard difficulty setter
def set_hard():
    game_loop(difficulty='hard')

    # hard difficulty setter

# police chase mode setter
def set_police():
    game_loop(difficulty='medium', police_chase=True)

# handle quitting the menu
def quit_menu():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# menu when game is lost
def close_game(snake_length):
    dis.fill(black)
    message("You lost! Press Q-Quit or C-Play Again", red)
    scoring_update(snake_length - 1)
    pygame.display.update()

# launch the menu
def main_menu():
    menu_active = True
    while menu_active:
        quit_menu()

        dis.fill(black)
        draw_button('Easy', 150, 250, 150, 50, dark_green, bright_green, set_easy)
        draw_button('Medium', 325, 250, 150, 50, blue, bright_blue, set_medium)
        draw_button('Hard', 500, 250, 150, 50, red, bright_red, set_hard)
        draw_button('Police chase', 675, 250, 200, 50, bright_blue, bright_red, set_police)

        pygame.display.update()

# run the game
main_menu()