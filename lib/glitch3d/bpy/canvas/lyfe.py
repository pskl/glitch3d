import uuid, sys, code, random, os, math, bpy, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Lyfe(canvas.Canvas):
    SIZE = 5

    def adjust_scale(self):
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                for z in range(self.SIZE):
                    if  self.cells[x][y][z] == 1 :
                        self.cubes[x][y][z].scale=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), random.uniform(0.4, 0.6))
                    else:
                        self.cubes[x][y][z].scale=(.1,.1,.1)
                    helpers.add_frame([self.cubes[x][y][z]], set(self.BAKED))

    def life(self, length):
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                for z in range(self.SIZE):
                    neighbors_alive_count = 0
                    for i in range(-1,2):
                        for j in range(-1,2):
                            for k in range( -1, 2):
                                x_index = (x + i + self.SIZE) % self.SIZE
                                y_index = (y + j + self.SIZE) % self.SIZE
                                z_index = (z + k + self.SIZE) % self.SIZE
                                print("Checking: " + str((x_index, y_index, z_index)) + " for: " + str((x, y, z)))
                                if not( x_index == x and y_index == y and z_index == z):
                                    neighbors_alive_count += self.cells[x_index][y_index][z_index]
                    if ( self.cells[x][y][z] == 1 and (neighbors_alive_count == 2 or neighbors_alive_count == 3)):
                        self.next_generation[x][y][z] = 1
                    elif ( self.cells[x][y][z] == 0 and neighbors_alive_count == 3 ):
                        self.next_generation[x][y][z] = 1
                    else:
                        self.next_generation[x][y][z] = 0
        for x in range(self.SIZE):
            for k in range(self.SIZE):
                for y in range(self.SIZE):
                    self.cells[x][y][z] = self.next_generation[x][y][z]
        self.adjust_scale()

    def render(self):
        DURATION=self.NUMBER_OF_FRAMES
        self.SCENE.frame_start = 0
        self.SCENE.frame_end = DURATION
        self.cubes = helpers.build_composite_object('Cube', self.SIZE-1, 0.5)

        self.cells = [[[ 0 for i in range(self.SIZE)] for k in range(self.SIZE)] for j in range(self.SIZE)]
        self.next_generation = [[[ 0 for i in range(self.SIZE)] for k in range(self.SIZE)] for j in range(self.SIZE)]

        for x in range(self.SIZE):
            for y in range(self.SIZE):
                for z in range(self.SIZE):
                    self.cubes[x][y][z].scale=(.1,.1,.1)
                    self.cells[x][y][z] = random.choice(range(2))
                    helpers.assign_material(self.cubes[x][y][z], helpers.random_material(self.MATERIALS_NAMES))

        print("Synthetic life begin")
        self.adjust_scale()
        for l in range(DURATION):
            self.SCENE.frame_set(l)
            print("Life in " + str(l))
            self.life(l)

