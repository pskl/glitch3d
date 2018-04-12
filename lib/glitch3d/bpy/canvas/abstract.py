import sys, code, random, os, math, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Abstract(canvas.Canvas):
  def render(self):
    base_model = self.SUBJECT

    for i in range(0, 5):
      copy = helpers.duplicate_object(base_model)
      copy.scale = helpers.rand_scale_vector(round(random.uniform(0, 1), 10))
      copy.location = helpers.rand_location()
      angles = [-90, 90, 0]
      self.props.append(copy)
      copy.rotation_euler.z += math.radians(random.choice(angles))
      copy.rotation_euler.y += math.radians(random.choice(angles))
      copy.rotation_euler.x += math.radians(random.choice(angles))
      copy.name = 'copy_' + str(i)
      helpers.assign_material(copy, helpers.random_material(self.MATERIALS_NAMES))

    # cut_copy = self.duplicate_object(self.SUBJECT)
    # self.cut(cut_copy)