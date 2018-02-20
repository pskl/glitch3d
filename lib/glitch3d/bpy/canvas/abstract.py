def render():
  # Create fractals of the same mesh
  base_model = SUBJECT

  # isometric_camera()

  curve = parametric_curve(random.choice(FUNCTIONS), random.choice(FUNCTIONS), random.choice(FUNCTIONS), 20)
  wireframize(curve, 1, 1)
  curve.name = 'param_curve'

  for i in range(0, 5):
    copy = duplicate_object(base_model)
    copy.scale = rand_scale_vector(round(random.uniform(0, 3), 10))
    copy.location = rand_location()
    angles = [-90, 90, 0]
    props.append(copy)
    copy.rotation_euler.z += math.radians(random.choice(angles))
    copy.rotation_euler.y += math.radians(random.choice(angles))
    copy.rotation_euler.x += math.radians(random.choice(angles))
    copy.name = 'copy_' + str(i)
    assign_material(copy, random_material())

