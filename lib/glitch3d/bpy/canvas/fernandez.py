# Matthew Plummer Fernandez hommage
# Draw interesting parametric curves and instantiate meshes on its path
import sys, code, random, os, math, bpy, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Fernandez(canvas.Canvas):
  MESH_NUMBER_LIMIT = 200 # otherwise Blender crashes
  MESH_OCCURENCE = 4 # 1 mesh every X point of the curve

  def rand_curve(self):
    return random.choice([
      # decorated knot
      [
        lambda t: math.cos( 2 * t * math.pi * 2 ) * ( 1 + 0.45 * math.cos( 3 * t * math.pi * 2 ) + 0.4 * math.cos( 9 * t * math.pi * 2 ) ),
        lambda t: math.sin( 2 * t * math.pi * 2 ) * ( 1 + 0.45 * math.cos( 3 * t * math.pi * 2 ) + 0.4 * math.cos( 9 * t * math.pi * 2 ) ),
        lambda t: 0.2 * math.sin( 9 * t * math.pi * 2 )
      ],
      # another knot like structure
      [
        lambda t: 10 * (math.cos(t) + math.cos(3 * t)) + math.cos(2 * t) + math.cos(4 * t),
        lambda t: 6 * math.sin(t) + 10 * math.sin(3 * t),
        lambda t: 4 * math.sin(3 * t) * math.sin(5 * t / 2) + 4 * math.sin(4 * t) - 2 * math.sin(6 * t)
      ],
      # Some weird sphere like structure (contained within a 1x1x1 cube)
      [
        lambda x: math.sin(x) * math.cos(20*x),
        lambda x: math.sin(x) * math.sin(20*x),
        lambda t: math.cos(t)
      ],
      # Some weird funnel like structure (contained within a 1x1x1 cube)
      [
        lambda x: math.sin(x) * math.cos(20*x),
        lambda x: math.sin(x) * math.sin(20*x),
        lambda t: math.sin(t)
      ]
    ])

  def render(self):
    rand_curve = helpers.create_line('rand_curve', helpers.parametric_curve(helpers.rand_proba(self.FUNCTIONS), helpers.rand_proba(self.FUNCTIONS), self.rand_proba(self.FUNCTIONS), 100, 100), random.choice(self.COLORS))
    rand_curve.scale = (2,2,2)
    helpers.glitch(rand_curve)
    art = self.matthew_curve(self.SUBJECT, 50)
    helpers.assign_material(art, helpers.random_material(self.MATERIALS_NAMES))

  def matthew_curve(self, obj, res, scale = 0.2):
    fx, fy, fz = self.rand_curve()
    verts = helpers.parametric_curve(fx, fy, fz, res, 1)
    i = res
    while len(verts[0::self.MESH_OCCURENCE]) > self.MESH_NUMBER_LIMIT:
      i -= 10
      print(str(i))
      verts = helpers.parametric_curve(fx, fy, fz, i, 1)
    self.SCENE.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for idx, coord in enumerate(verts[0::self.MESH_OCCURENCE]):
      new_obj = helpers.duplicate_object(obj)
      new_obj.select = True
      new_obj.location = coord
      # new_obj.location = tuple([scale*x for x in coord]) # scale down the vertices
      new_obj.scale = (0.02,0.02,0.02) if idx % 2 == 0 else (0.05, 0.05, 0.05)
      new_obj.rotation_euler.z += idx * (2 * math.pi) / len(verts)
      self.SCENE.objects.active = new_obj
    bpy.ops.object.join()
    res = self.SCENE.objects.active
    res.name = 'fernandez'
    helpers.resize(res)
    tracker = helpers.create_line('fernandez_tracker', verts, random.choice(self.COLORS), 0.05, location=self.ORIGIN)
    edges = []
    for v in range(0, (len(verts) - 1)):
        edges.append([v, v+1])
    res = helpers.create_mesh('fernandez', verts, [], (0,0,0), edges)
    tracker.rotation_euler.x += math.radians(90)
    tracker.scale = (scale, scale, scale)
    return tracker
