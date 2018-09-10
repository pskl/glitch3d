# Use noise to animate some objects in wave pattern
import sys, code, random, os, math, bpy, canvas, colorsys
from math import sqrt, pi, sin, ceil
from random import TWOPI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Waves(canvas.Canvas):

  COUNT=10

  def render(self):
    count = self.COUNT
    # Size of grid.
    extents = 8.0
    # The height of each cube will be animated, so we'll specify the minimum and maximum scale.
    sz = (extents / count)
    base_object = helpers.infer_primitive(random.choice(self.PRIMITIVES), location = (100, 100, 100), radius=sz)
    helpers.assign_material(base_object, helpers.random_material(self.MATERIALS_NAMES))
    minsz = sz * 0.25
    maxsz = sz * extents
    # To convert abstract grid position within loop to real-world coordinate.
    jprc = 0.0
    kprc = 0.0
    countf = 1.0 / (count - 1)
    diffex = extents * 2
    y = 0.0
    x = 0.0
    centerz = 0.0
    centery = 0.0
    centerx = 0.0
    # The maximum possible distance is used to normalize the distance.
    rise = 0.0
    run = 0.0
    normdist = 0.0
    maxdist = sqrt(2 * extents * extents)
    # For generating the wave.
    offset = 0.0
    angle = 0.0
    # Loop through grid y axis.
    for j in range(0, count, 1):
      jprc = j * countf
      y = -extents + jprc * diffex
      # Calculate rise.
      rise = y - centery
      rise *= rise
      # Loop through grid x axis.
      for k in range(0, count, 1):
        kprc = k * countf
        x = -extents + kprc * diffex
        # Calculate run.
        run = x - centerx
        run *= run
        # Find normalized distance using Pythogorean theorem.
        # Remap the normalized distance to a range -PI .. PI
        normdist = sqrt(rise + run) / maxdist
        offset = -TWOPI * normdist + pi
        current = helpers.duplicate_object(base_object)
        current.location = (centerx + x, centery + y, centerz)
        current.name = 'Object ({0:0>2d}, {1:0>2d})'.format(k, j)
        current.data.name = 'Mesh ({0:0>2d}, {1:0>2d})'.format(k, j)
        for f in range(0, self.NUMBER_OF_FRAMES, 1):
          # Convert the keyframe into an angle.
          fprc = f * 1.0 / (self.NUMBER_OF_FRAMES - 1)
          angle = TWOPI * fprc
          # Set the scene to the current frame.
          bpy.context.scene.frame_set(f)
          # Change the scale.
          # sin returns a value in the range -1 .. 1. abs changes the range to 0 .. 1.
          # The values are remapped to the desired scale with min + percent * (max - min).
          current.scale.z = minsz + abs(sin(offset + angle)) * (maxsz - minsz)
          helpers.add_frame([current], ['scale'])
