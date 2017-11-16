# Square wall art resolution: 10200x10200 (threadless, society6)
def set_tile(size):
    SCENE.render.tile_x = size
    SCENE.render.tile_y = size

def render_settings(animate, mode):
    SCENE.render.resolution_x = 2000
    SCENE.render.resolution_y = 2000
    SCENE.render.engine = 'CYCLES'
    SCENE.render.resolution_percentage = 25

    # bpy.SCENE.cycles.device = 'GPU'
    SCENE.render.image_settings.compression = 90
    SCENE.cycles.samples = 20
    SCENE.cycles.max_bounces = 1
    SCENE.cycles.min_bounces = 1
    SCENE.cycles.caustics_reflective = False
    SCENE.cycles.caustics_refractive = False

    SCENE.render.image_settings.color_mode ='RGBA'
    SCENE.render.layers[0].cycles.use_denoising = True
    set_tile(32)

    if animate:
        SCENE.render.image_settings.file_format='AVI_RAW'
    else:
        SCENE.render.image_settings.file_format='PNG'

    if mode == 'high':
        set_tile(64)
        SCENE.cycles.samples = 100
        SCENE.render.resolution_percentage = 100

