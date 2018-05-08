# Use noise to animate some objects in wave pattern
import sys, code, random, os, math, bpy, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Wave(canvas.Canvas):

  def render(self):
    print("lol")