import sys, code, random, os, math, canvas, bpy, mathutils

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Abstract(canvas.Canvas):
  def render(self):
    copies = []
    for i in range(0, 10):
      copy = helpers.load_random_obj(self.MODELS_FOLDER_PATH)
      angles = [-90, 90, 0]
      copy.rotation_euler = mathutils.Vector((math.radians(random.choice(angles)), math.radians(random.choice(angles)), math.radians(random.choice(angles))))
      copies.append(copy)
      copy.name = "copy_abstract_piece_" + str(i)
      helpers.resize(copy)
      helpers.assign_material(copy, helpers.random_material(self.MATERIALS_NAMES))

    self.SUBJECT.location.y += random.uniform(1, 2)
    helpers.cut(helpers.duplicate_object(self.SUBJECT))

    for f in range(self.NUMBER_OF_FRAMES):
      bpy.context.scene.frame_set(f)
      for copy in copies:
        helpers.shuffle(copy, self.CANVAS_BOUNDARY)
      helpers.add_frame(copies, ['location'])