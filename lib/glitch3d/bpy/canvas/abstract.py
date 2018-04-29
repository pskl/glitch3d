import sys, code, random, os, math, canvas, bpy

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Abstract(canvas.Canvas):
  def render(self):
    base_model = self.SUBJECT

    for i in range(0, 10):
      copy = self.load_random_obj()
      copy.scale = helpers.rand_scale_vector(round(random.uniform(0, 1), 10))
      copy.location = helpers.rand_location()
      angles = [-90, 90, 0]
      self.props.append(copy)
      copy.rotation_euler.z += math.radians(random.choice(angles))
      copy.rotation_euler.y += math.radians(random.choice(angles))
      copy.rotation_euler.x += math.radians(random.choice(angles))
      copy.name = 'copy_' + str(i)
      helpers.assign_material(copy, helpers.random_material(self.MATERIALS_NAMES))

    cut_copy = self.duplicate_object(self.SUBJECT)
    self.cut(cut_copy)

  def load_random_obj(self):
    objs = []
    for f in os.listdir(self.FIXTURES_FOLDER_PATH):
      if f.endswith('.obj') and not f.endswith('_glitched.obj'):
        objs.append(f)
    bpy.ops.import_scene.obj(filepath = self.FIXTURES_FOLDER_PATH + random.choice(objs), use_edges=True)
    return bpy.context.selected_objects[0]