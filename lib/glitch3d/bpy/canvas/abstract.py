import sys, code, random, os, math

sys.path.append(os.path.dirname(__file__) + '/canvas.py')
canvas = __import__('canvas')

class Abstract(canvas.Canvas):
  def render(self):
    curve = self.parametric_curve(random.choice(self.FUNCTIONS), random.choice(self.FUNCTIONS), random.choice(self.FUNCTIONS), 20)
    base_model = self.SUBJECT
    # self.isometric_camera()
    self.wireframize(curve, 1, 1)
    curve.name = 'param_curve'

    for i in range(0, 5):
      copy = self.duplicate_object(base_model)
      copy.scale = self.rand_scale_vector(round(random.uniform(0, 3), 10))
      copy.location = self.rand_location()
      angles = [-90, 90, 0]
      self.props.append(copy)
      copy.rotation_euler.z += math.radians(random.choice(angles))
      copy.rotation_euler.y += math.radians(random.choice(angles))
      copy.rotation_euler.x += math.radians(random.choice(angles))
      copy.name = 'copy_' + str(i)
      self.assign_material(copy, self.random_material())
