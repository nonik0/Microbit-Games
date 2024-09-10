from microbit import *
from random import *
import random

# tilt: navigate maze
# A button: toggle vertical or horizontal orientation
# B button: change difficulty

SCREEN_SIZE = 5
JOY_TOLERANCE = 250
orientation = False # determines x or z for second rotational axis
difficulty = 0
difficulty_sizes = [(4,4), (4,8), (8,8)]

def shuffle_list(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]
    
    return lst

def find_start_point(maze):
    """Randomly choose a point just inside the outer wall (1 row/column in)."""
    width = len(maze[0])
    height = len(maze)
    possible_start_point = []
    for y in range(1, height - 1):
        if not maze[y][1]:
            possible_start_point.append((1, y))  # Left side
        if not maze[y][width - 2]:
            possible_start_point.append((width - 2, y))  # Right side
    for x in range(1, width - 1):
        if not maze[1][x]:
            possible_start_point.append((x, 1))  # Top side
        if not maze[height - 2][x]:
            possible_start_point.append((x, height - 2))  # Bottom side
    return choice(possible_start_point) if possible_start_point else (1, 1)

def find_end_point(maze):
    """Find an appropriate end point for the maze (a dead-end with 3 walls around it)."""
    width = len(maze[0])
    height = len(maze)
    possible_end_point = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not maze[y][x]:
                # Count how many walls surround this cell
                walls = 0
                if maze[y-1][x]: walls += 1
                if maze[y+1][x]: walls += 1
                if maze[y][x-1]: walls += 1
                if maze[y][x+1]: walls += 1
                if walls == 3:
                    possible_end_point.append((x, y))

    # Choose a random dead-end as the end point
    return choice(possible_end_point) if possible_end_point else (width - 2, height - 2)

def make_maze(w, h):
    # Create a grid filled with walls (walls are True, empty cells are False)
    maze = [[True for _ in range(2*w+1)] for _ in range(2*h+1)]

    # Define the starting point
    x, y = (0, 0)
    maze[2*y+1][2*x+1] = False

    # Initialize the stack with the starting point
    stack = [(x, y)]
    while len(stack) > 0:
        x, y = stack[-1]

        # Define possible directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        shuffle_list(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if nx >= 0 and ny >= 0 and nx < w and ny < h and maze[2*ny+1][2*nx+1] == 1:
                maze[2*ny+1][2*nx+1] = False
                maze[2*y+1+dy][2*x+1+dx] = False
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    return maze

while True: # game loop
    dim_x, dim_y = difficulty_sizes[difficulty]
    maze = make_maze(dim_x, dim_y)
    maze_width = len(maze[0])
    maze_height = len(maze)
    player_x, player_y = find_start_point(maze)
    exit_x, exit_y = find_end_point(maze)
    loop = 0
    
    while True: # maze loop
        view_x = min(max(player_x - SCREEN_SIZE//2, 0),maze_width - SCREEN_SIZE)
        view_y = min(max(player_y - SCREEN_SIZE//2, 0),maze_height - SCREEN_SIZE)
    
        # draw maze
        for display_x in range(SCREEN_SIZE):
            for display_y in range(SCREEN_SIZE):
                display.set_pixel(display_x, display_y, 9 if maze[view_y + display_y][view_x + display_x] else 0)
    
        # draw player
        display_x = player_x - view_x
        display_y = player_y - view_y 
        if display_x in range(SCREEN_SIZE) and display_y in range(SCREEN_SIZE):
            if loop % 2:
                display.set_pixel(display_x, display_y, 5)
            else:
                display.set_pixel(display_x, display_y, 0)
    
        # draw exit
        display_x = exit_x - view_x
        display_y = exit_y - view_y 
        if display_x in range(SCREEN_SIZE) and display_y in range(SCREEN_SIZE):
            display.set_pixel(display_x, display_y, random.randint(1, 9)) # simple flicker effect

        # win condition
        if player_x == exit_x and player_y == exit_y:
            break
    
        if button_a.was_pressed():
            orientation = not orientation

        if button_b.was_pressed():
            difficulty = (difficulty + 1) % len(difficulty_sizes)  
            break
            
        joy_x = accelerometer.get_x()
        joy_y = accelerometer.get_y() if orientation else accelerometer.get_z()
    
        if joy_y < -JOY_TOLERANCE:
            delta_y = -1
        elif joy_y > JOY_TOLERANCE:
            delta_y = 1
        else:
            delta_y = 0
    
        if joy_x < -JOY_TOLERANCE:
            delta_x = -1
        elif joy_x > JOY_TOLERANCE:
            delta_x = 1
        else:
            delta_x = 0
    
        if delta_x != 0 and delta_y != 0:
            if abs(joy_x) > abs(joy_y):
                delta_y = 0
            else:
                delta_x = 0
    
        # move player if input
        if (delta_x != 0 or delta_y != 0) and loop % 4 == 0: # slow down movement
            new_player_x = player_x + delta_x
            new_player_y = player_y + delta_y
    
            if new_player_x in range(maze_width) and new_player_y in range(maze_height) and not maze[new_player_y][new_player_x]:
                player_x = new_player_x
                player_y = new_player_y
    
        loop = (loop + 1) % 20
        sleep(100)
        # end maze loop
    
    sleep(500)
    display.clear()
    if player_x == exit_x and player_y == exit_y:
        display.scroll('WIN!')
    elif difficulty is 0:
        display.scroll ('4x4')
    elif difficulty is 1:
        display.scroll ('4x8')
    elif difficulty is 2:
        display.scroll ('8x8')
    # end game loop