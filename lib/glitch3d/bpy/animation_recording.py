scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end   = NUMBER_OF_FRAMES
bpy.ops.screen.frame_jump(end=False)

for frame in range(1, NUMBER_OF_FRAMES):
    bpy.context.scene.frame_set(frame)
    # do stuff here
    for ob in context.scene.objects:
        ob.keyframe_insert(data_path="location", index=-1)

bpy.ops.screen.frame_jump(end=False)