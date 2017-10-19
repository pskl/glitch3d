######################
## FLUID SIMULATION ##
######################
animate = True
context.scene.frame_end = NUMBER_OF_FRAMES

# Container
bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=7)
container = bpy.data.objects['Cube']
container.name = 'Container'
container.modifiers.new(name='container', type='FLUID_SIMULATION')
container.modifiers['container'].settings.type = 'DOMAIN'
container.modifiers['container'].settings.generate_particles = 1
make_object_gradient_fabulous(container, rand_color(), rand_color())
container.location = (0, 0, 7)

# Emitter of fluid
bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,10))
emitter = bpy.data.objects['Sphere']
emitter.name = 'Emitter'
emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
emitter.modifiers['emitter'].settings.type = 'INFLOW'
emitter.modifiers['emitter'].settings.inflow_velocity = mathutils.Vector((0, 0, -1))
emitter.scale = (0.5, 0.5, 0.5)

SUBJECT.modifiers.new(name='obstacle', type='FLUID_SIMULATION')
SUBJECT.modifiers['obstacle'].settings.type = 'OBSTACLE'
SUBJECT.modifiers['obstacle'].settings.volume_initialization = 'BOTH'
SUBJECT.modifiers['obstacle'].settings.surface_subdivisions = 6
SUBJECT.modifiers['obstacle'].settings.partial_slip_factor = 0.15

# Bake animation
bpy.ops.fluid.bake({'scene': context.scene, 'active_object': container})