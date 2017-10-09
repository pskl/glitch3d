def render_settings(scene, animate, mode):
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 2000
    scene.render.engine = 'CYCLES'
    scene.render.resolution_percentage = 25

    # bpy.scene.cycles.device = 'GPU'
    scene.render.image_settings.compression = 0
    scene.cycles.samples = 25
    scene.cycles.max_bounces = 1
    scene.cycles.min_bounces = 1
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.render.tile_x = 32
    scene.render.tile_y = 32
    scene.render.image_settings.color_mode ='RGBA'

    if animate:
        scene.render.image_settings.file_format='H264'
    else:
        scene.render.image_settings.file_format='PNG'

    if mode == 'high':
        scene.render.image_settings.compression = 90
        scene.cycles.samples = 400
        scene.render.resolution_percentage = 100