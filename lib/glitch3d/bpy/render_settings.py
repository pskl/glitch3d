context.scene.render.resolution_x = 2000
context.scene.render.resolution_y = 2000
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_percentage = 25

# bpy.context.scene.cycles.device = 'GPU'
context.scene.render.image_settings.compression = 0
context.scene.cycles.samples = 25
context.scene.cycles.max_bounces = 1
context.scene.cycles.min_bounces = 1
context.scene.cycles.caustics_reflective = False
context.scene.cycles.caustics_refractive = False
context.scene.render.tile_x = 32
context.scene.render.tile_y = 32
context.scene.render.image_settings.color_mode ='RGBA'

if ANIMATE:
    context.scene.render.image_settings.file_format='H264'
else:
    context.scene.render.image_settings.file_format='PNG'

if mode == 'high':
    context.scene.render.image_settings.compression = 90
    context.scene.cycles.samples = 400
    context.scene.render.resolution_percentage = 100