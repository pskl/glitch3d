# Conway's game of life in 3D, each cube having 27 neighboring cubes at most
import uuid, sys, code, random, os, math, bpy, canvas, mathutils, numpy

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Lyfe(canvas.Canvas):
    SIZE = 5

    def render(self):
        self.cubes = helpers.build_composite_object('Cube', self.SIZE-1, 0.5)
        for a in self.cubes:
          for b in a:
            for c in b:
              c.location += mathutils.Vector((self.SIZE/2, self.SIZE/2, self.SIZE/2))
        self.cells = [[[ 0 for i in range(self.SIZE)] for k in range(self.SIZE)] for j in range(self.SIZE)]
        self.next_generation = [[[ 0 for i in range(self.SIZE)] for k in range(self.SIZE)] for j in range(self.SIZE)]

        for x in range(self.SIZE):
            for y in range(self.SIZE):
                for z in range(self.SIZE):
                    self.cubes[x][y][z].scale=(.1,.1,.1)
                    self.cells[x][y][z] = numpy.random.choice([0, 1], 1, p=[0.6, 0.4])[0]
                    helpers.assign_material(self.cubes[x][y][z], helpers.random_material(self.MATERIALS_NAMES))

        print("Synthetic life begin")
        self.adjust_scale()
        for l in range(self.NUMBER_OF_FRAMES):
            bpy.context.scene.frame_set(l)
            print("Life in " + str(l))
            self.life(l)

    def adjust_scale(self):
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                for z in range(self.SIZE):
                    if  self.cells[x][y][z] == 1 :
                        self.cubes[x][y][z].scale=(random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), random.uniform(0.4, 0.6))
                    else:
                        self.cubes[x][y][z].scale=(0,0,0)
                    helpers.add_frame([self.cubes[x][y][z]], ["scale"])

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
                                if not( x_index == x and y_index == y and z_index == z):
                                    neighbors_alive_count += self.cells[x_index][y_index][z_index]
                    if self.cells[x][y][z] == 1 and neighbors_alive_count > 6:
                        self.next_generation[x][y][z] = 1 # maintenance
                    elif self.cells[x][y][z] == 0 and neighbors_alive_count > 10:
                        self.next_generation[x][y][z] = 1 # come alive
                    elif self.cells[x][y][z] == 1 and neighbors_alive_count > 10:
                      self.next_generation[x][y][z] = 0 # overpopulation
                    elif self.cells[x][y][z] == 1 and neighbors_alive_count < 6:
                        self.next_generation[x][y][z] = 0 # underpopulation
        self.cells = self.next_generation
        self.adjust_scale()
