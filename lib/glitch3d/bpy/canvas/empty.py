import sys, code, random, os, math, bpy, mathutils, uuid, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Empty(canvas.Canvas):
  def render(self):
    return True