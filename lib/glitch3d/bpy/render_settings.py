# Square wall art resolution: 10200x10200 (threadless, society6)
def render_settings(animate, mode):
    SCENE.render.resolution_x = 2000
    SCENE.render.resolution_y = 2000
    SCENE.render.engine = 'CYCLES'
    SCENE.render.resolution_percentage = 25

    # bpy.SCENE.cycles.device = 'GPU'
    SCENE.render.image_settings.compression = 0
    SCENE.cycles.samples = 25
    SCENE.cycles.max_bounces = 1
    SCENE.cycles.min_bounces = 1
    SCENE.cycles.caustics_reflective = False
    SCENE.cycles.caustics_refractive = False
    SCENE.render.tile_x = 32
    SCENE.render.tile_y = 32
    SCENE.render.image_settings.color_mode ='RGBA'
    SCENE.render.layers[0].cycles.use_denoising = True

    if animate:
        SCENE.render.image_settings.file_format='AVI_RAW'
    else:
        SCENE.render.image_settings.file_format='PNG'

    if mode == 'high':
        SCENE.render.image_settings.compression = 90
        SCENE.cycles.samples = 400
        SCENE.render.resolution_percentage = 100