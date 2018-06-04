def make_world_volumetric(world, scatter_intensity = SCATTER_INTENSITY, absorption_intensity = ABSORPTION_INTENSITY):
    assert world.use_nodes == True
    output = world.node_tree.nodes['World Output']
    bg_node = world.node_tree.nodes.new('ShaderNodeBackground')
    absorption_node = world.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
    scatter_node = world.node_tree.nodes.new('ShaderNodeVolumeScatter')
    add_shader = world.node_tree.nodes.new('ShaderNodeAddShader')
    world.node_tree.links.new(add_shader.outputs[0], output.inputs['Volume'])
    world.node_tree.links.new(bg_node.outputs['Background'], output.inputs['Surface'])
    world.node_tree.links.new(scatter_node.outputs[0], add_shader.inputs[0])
    world.node_tree.links.new(absorption_node.outputs[0], add_shader.inputs[1])
    scatter_node.inputs['Density'].default_value = SCATTER_INTENSITY
    absorption_node.inputs['Density'].default_value = ABSORPTION_INTENSITY
    bg_node.inputs[0].default_value = random.choice(COLORS)

def render_normals():
    bpy.context.scene.render.engine = 'BLENDER_RENDER' # No need for raytracing if only rendering normals
    bpy.context.scene.use_nodes = True
    bpy.context.scene.render.layers[0].use_pass_normal = True
    bpy.context.scene.render.layers[0].use_pass_z = False
    bpy.context.scene.render.layers[0].use_pass_combined = False
    node_tree = bpy.context.scene.node_tree
    enter = node_tree.nodes.new('CompositorNodeRLayers')
    composite = node_tree.nodes['Composite']
    multiply = node_tree.nodes.new('CompositorNodeMixRGB')
    add = node_tree.nodes.new('CompositorNodeMixRGB')
    multiply.blend_type = "MULTIPLY"
    add.blend_type = 'ADD'
    add.inputs[1].default_value = random.choice(COLORS)
    multiply.inputs[1].default_value = random.choice(COLORS)
    invert = node_tree.nodes.new('CompositorNodeInvert')
    node_tree.links.new(add.outputs[0], invert.inputs[1])
    node_tree.links.new(multiply.outputs[0], add.inputs[2])
    node_tree.links.new(enter.outputs['Normal'], multiply.inputs[1])
    node_tree.links.new(invert.outputs[0], composite.inputs[0])

def isometric_camera():
    CAMERA.location = (12, -12, 12)
    CAMERA.rotation_euler = (54.8, 0, 45)
    CAMERA.data.type = 'ORTHO'
    FIXED_CAMERA = True

# Split rendering into 3 rendering layers
def split_into_render_layers(debug=False):
    if debug:
      bpy.context.scene.render.layers[0].use = False
      bpy.context.scene.render.layers[1].use = True
      bpy.context.scene.render.layers[2].use = False
      bpy.context.scene.render.layers[3].use = False
      for obj in bpy.data.objects:
        obj.layers[0] = False
        obj.layers[1] = True
      return None
    else:
      bpy.context.scene.render.layers[0].use = False
      chunks = chunk_it(bpy.data.objects, 3)
      for chunk_index in range(len(chunks)):
          for obj in chunks[chunk_index]:
              obj.layers[chunk_index + 1] = True
              obj.layers[0] = False
      for l in bpy.context.scene.render.layers[1:4]:
          l.use = True
      for obj in bpy.data.objects:
          assert obj.layers[0] == False
          assert len([i for i, x in enumerate(list(obj.layers)) if x]) == 1 # Only 1 layer activated
      assert bpy.context.scene.render.layers[0].use == False
      assert bpy.context.scene.render.layers[1].use == True
      bpy.context.scene.layers[1] = True
      bpy.context.scene.layers[2] = True
      bpy.context.scene.layers[3] = True

def render_settings(animate, mode, normals, width, height, debug):
    for layer in bpy.context.scene.render.layers:
      layer.use_pass_ambient_occlusion = True
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    bpy.context.scene.render.resolution_percentage = 25
    bpy.context.scene.render.image_settings.compression = 90
    bpy.context.scene.cycles.samples = 20
    bpy.context.scene.cycles.max_bounces = 1
    CAMERA.data.dof_distance = (SUBJECT.location - CAMERA.location).length
    bpy.context.scene.cycles.shading_system = OSL_ENABLED
    bpy.context.scene.cycles.min_bounces = 1
    bpy.context.scene.cycles.caustics_reflective = False
    bpy.context.scene.cycles.caustics_refractive = False
    bpy.context.scene.cycles.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode ='RGBA'
    if not debug:
      bpy.context.scene.render.layers[1].cycles.use_denoising = True
      bpy.context.scene.render.layers[2].cycles.use_denoising = True
      bpy.context.scene.render.layers[3].cycles.use_denoising = True
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Filmic - High Contrast"
    tile_size = int(width / 30)
    bpy.context.scene.render.tile_x = tile_size
    bpy.context.scene.render.tile_y = tile_size
    if normals:
        render_normals() # 1 render layer
    else:
      split_into_render_layers(debug)
    if animate:
        bpy.context.scene.render.image_settings.file_format='AVI_RAW'
    else:
        bpy.context.scene.render.image_settings.file_format='PNG'
    if mode == 'high':
        bpy.context.scene.cycles.samples = 100
        bpy.context.scene.render.resolution_percentage = 100



