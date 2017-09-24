context.scene.frame_start = 0
context.scene.frame_end   = NUMBER_OF_FRAMES
bpy.ops.screen.frame_jump(end=False)

for frame in range(1, NUMBER_OF_FRAMES):
    bpy.context.scene.frame_set(frame)

    OCEAN.modifiers['Ocean'].time += 1
    model_object.rotation_euler.z += math.radians(10)

    for ob in context.scene.objects:
        ob.keyframe_insert(data_path="location", index=-1)

bpy.ops.screen.frame_jump(end=False)