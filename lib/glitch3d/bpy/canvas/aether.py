import sys, code, random, os, math, bpy, mathutils, uuid, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Aether(canvas.Canvas):
  def render(self):
    RADIUS=5
    ######################
    ## SMOKE SIMULATION ##
    ######################
    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 4.0),radius=RADIUS)
    container = bpy.context.object
    container.name = 'smoke_container'
    container.modifiers.new(name='container', type='SMOKE')
    container.modifiers['container'].smoke_type = 'DOMAIN'
    container.modifiers['container'].domain_settings.use_high_resolution = True
    container.modifiers['container'].domain_settings.vorticity = 3
    container.modifiers['container'].domain_settings.vorticity = 3
    container.modifiers["container"].domain_settings.alpha = - 1.2
    helpers.assign_material(container, bpy.data.materials['Smoke Domain Material'])
    emitter = self.spawn_emitter_smoke(self.ORIGIN)
    self.make_object_smoke_collider(self.SUBJECT)

    emitter.modifiers["emitter"].flow_settings.density = 1
    bpy.context.scene.frame_set(0)
    emitter.location = helpers.rand_location(7, positive=True)
    helpers.add_frame([emitter], ['location'])
    bpy.context.scene.frame_set(self.NUMBER_OF_FRAMES)
    emitter.location = (4,4,4)
    helpers.add_frame([emitter], ['location'])

  def spawn_emitter_smoke(self, location, obj = None):
    bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    emitter = bpy.context.object
    emitter.cycles_visibility.camera = False
    emitter.name = 'smoke_emitter_' + str(uuid.uuid1())
    emitter.modifiers.new(name='emitter', type='SMOKE')
    emitter.modifiers['emitter'].smoke_type = 'FLOW'
    emitter.modifiers['emitter'].flow_settings.smoke_color = (helpers.rand_color_value(), helpers.rand_color_value(), helpers.rand_color_value())
    emitter.modifiers['emitter'].flow_settings.temperature = 1
    emitter.scale = (0.4,0.4,0.4)
    return emitter

  def make_object_smoke_collider(self, obj):
      obj.modifiers.new(name='obstacle', type='SMOKE')
      obj.modifiers['obstacle'].smoke_type = 'COLLISION'

