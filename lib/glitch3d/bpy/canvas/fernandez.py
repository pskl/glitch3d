# Matthew Plummer Fernandez hommage
import sys, code, random, os, math, bpy, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Fernandez(canvas.Canvas):
  def render(self):
    # rand_curve = helpers.create_line('rand_curve', helpers.parametric_curve(helpers.rand_proba(self.FUNCTIONS), helpers.rand_proba(self.FUNCTIONS), self.rand_proba(self.FUNCTIONS), 100, 100), random.choice(self.COLORS))
    # rand_curve.scale = (2,2,2)
    # helpers.glitch(rand_curve)
    art = self.matthew_curve(self.SUBJECT)
    # helpers.assign_material(art, helpers.random_material(self.MATERIALS_NAMES))

  def matthew_curve(self, obj):
    fx = lambda t: 10 * (math.cos(t) + math.cos(3 * t)) + math.cos(2 * t) + math.cos(4 * t)
    fy = lambda t: 6 * math.sin(t) + 10 * math.sin(3 * t)
    fz = lambda t: 4 * math.sin(3 * t) * math.sin(5 * t / 2) + 4 * math.sin(4 * t) - 2 * math.sin(6 * t)
    verts = helpers.parametric_curve(fx, fy, fz, 200)
    self.SCENE.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    # for idx, coord in enumerate(verts[0::2]):
    #   new_obj = helpers.duplicate_object(obj)
    #   new_obj.select = True
    #   new_obj.location = coord
    #   new_obj.scale = (0.02,0.02,0.02) if idx % 2 == 0 else (0.05, 0.05, 0.05)
    #   new_obj.rotation_euler.z += idx * (2 * math.pi) / len(verts)
    #   self.SCENE.objects.active = new_obj
    # bpy.ops.object.join()
    # res = self.SCENE.objects.active
    # res.name = 'matthew'
    # return res
    helpers.create_line('matthew', verts, random.choice(self.COLORS))
