# Game of life inspired scene
SIZE = 5
DURATION=NUMBER_OF_FRAMES
SCENE.frame_start = 0
SCENE.frame_end = DURATION
cubes = build_composite_object('CUBE', SIZE-1, 0.5)

cells = [[[ 0 for i in range(SIZE)] for k in range(SIZE)] for j in range(SIZE)]
next_generation = [[[ 0 for i in range(SIZE)] for k in range(SIZE)] for j in range(SIZE)]

for x in range(SIZE):
    for y in range(SIZE):
        for z in range(SIZE):
            cubes[x][y][z].scale=(.1,.1,.1)
            cells[x][y][z] = random.choice(range(2))
            make_object_gradient_fabulous(cubes[x][y][z], rand_color(), rand_color())

def adjust_scale():
    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):
                if  cells[x][y][z] == 1 :
                    cubes[x][y][z].scale=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), random.uniform(0.4, 0.6))
                else:
                    cubes[x][y][z].scale=(.1,.1,.1)
                add_frame([cubes[x][y][z]])

def life(l):
    print("Life in " + str(l))
    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):
                neighbors_alive_count = 0
                for i in range(-1,2):
                    for j in range(-1,2):
                        for k in range( -1, 2):
                            x_index = (x + i + SIZE) % SIZE
                            y_index = (y + j + SIZE) % SIZE
                            z_index = (z + k + SIZE) % SIZE
                            print("Checking: " + str((x_index, y_index, z_index)) + " for: " + str((x, y, z)))
                            if not( x_index == x and y_index == y and z_index == z):
                                neighbors_alive_count += cells[x_index][y_index][z_index]
                if ( cells[x][y][z] == 1 and (neighbors_alive_count == 2 or neighbors_alive_count == 3)):
                    next_generation[x][y][z] = 1
                elif ( cells[x][y][z] == 0 and neighbors_alive_count == 3 ):
                    next_generation[x][y][z] = 1
                else:
                    next_generation[x][y][z] = 0
    for x in range(SIZE):
        for k in range(SIZE):
            for y in range(SIZE):
                cells[x][y][z] = next_generation[x][y][z]
    adjust_scale()

print("Synthetic life begin")
adjust_scale()
for l in range(DURATION):
    SCENE.frame_set(l)
    life(l)

