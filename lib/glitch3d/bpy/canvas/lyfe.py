# Game of life inspired scene
SIZE = 10
DURATION=NUMBER_OF_FRAMES
SCENE.frame_start = 0
SCENE.frame_end = DURATION
cubes = build_grid_object('CUBE', SIZE-1, 0.5, 1)

cells = [[ 0 for i in range(SIZE)] for j in range(SIZE)]
next_generation = [[ 0 for i in range(SIZE)] for j in range(SIZE)]

for x in range(SIZE):
    for y in range(SIZE):
        cubes[x][y].scale=(.1,.1,.1)
        cells[x][y] = random.choice(range(2))
        make_object_gradient_fabulous(cubes[x][y], rand_color(), rand_color())

def adjust_scale():
    for x in range(SIZE):
        for y in range(SIZE):
            if  cells[x][y] == 1 :
                cubes[x][y].scale=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), random.uniform(0.4, 0.6))
            else:
                cubes[x][y].scale=(.2,.2,.2)
            for line in cubes:
                add_frame(line)

def life(l):
    print("Life in " + str(l))
    for x in range(SIZE):
        for y in range(SIZE):
            neighbors_alive_count = 0
            for i in range(-1,2):
                for j in range( -1, 2):
                    x_index = (x + i + SIZE) % SIZE
                    y_index = (y + j + SIZE) % SIZE
                    if not( x_index == x and y_index == y):
                        neighbors_alive_count += cells[x_index][y_index]
            if ( cells[x][y] == 1 and (neighbors_alive_count == 2 or neighbors_alive_count == 3)):
                next_generation[x][y] = 1
            elif ( cells[x][y] == 0 and neighbors_alive_count == 3 ):
                next_generation[x][y] = 1
            else:
                next_generation[x][y] = 0
    for x in range(SIZE):
        for y in range(SIZE):
            cells[x][y] = next_generation[x][y]
    adjust_scale()

print("Synthetic life begin")
adjust_scale()
for l in range(DURATION):
    SCENE.frame_set(l)
    life(l)

