# Use noise to animate some objects in wave pattern
import sys, code, random, os, math, bpy, canvas, colorsys
from math import sqrt, pi, sin, ceil
from random import TWOPI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Waves(canvas.Canvas):
  def render(self):
    count = 16
    # Size of grid.
    extents = 8.0
    # Spacing between cubes.
    padding = 0.002
    # Size of each cube.
    # The height of each cube will be animated, so we'll specify the minimum and maximum scale.
    sz = (extents / count) - padding
    base_object = helpers.infer_primitive(random.choice(self.PRIMITIVES), location = (100, 100, 100), radius=sz)
    minsz = sz * 0.25
    maxsz = sz * extents
    diffsz = maxsz - minsz
    # To convert abstract grid position within loop to real-world coordinate.
    jprc = 0.0
    kprc = 0.0
    countf = 1.0 / (count - 1)
    diffex = extents * 2
    # Position of each cube.
    y = 0.0
    x = 0.0
    # Center of grid.
    centerz = 0.0
    centery = 0.0
    centerx = 0.0
    # Distances of cube from center.
    # The maximum possible distance is used to normalize the distance.
    rise = 0.0
    run = 0.0
    normdist = 0.0
    maxdist = sqrt(2 * extents * extents)
    # For animation, track current frame, specify desired number of key frames.
    invfcount = 1.0 / (self.NUMBER_OF_FRAMES - 1)
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
          fprc = f * invfcount
          angle = TWOPI * fprc
          # Set the scene to the current frame.
          bpy.context.scene.frame_set(f)
          # Change the scale.
          # sin returns a value in the range -1 .. 1. abs changes the range to 0 .. 1.
          # The values are remapped to the desired scale with min + percent * (max - min).
          current.scale[2] = minsz + abs(sin(offset + angle)) * diffsz
          # Insert the key frame for the scale property.
          current.keyframe_insert(data_path='scale', index=2)
          # Advance by the keyframe increment to the next keyframe.
