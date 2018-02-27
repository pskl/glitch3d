import uuid, sys, code, random, os, math, bpy

sys.path.append(os.path.dirname(__file__) + '/canvas.py')
canvas = __import__('canvas')

class Frame(canvas.Canvas):
    # generate line -> rotate 45 degrees -> extrude -> mirror end -> cursor to center -> mirror
    def spawn_frame(self, segment, side = 20):
        profile = segment
        profile.name = 'frame_' + str(uuid.uuid1())
        profile.rotation_euler.z -= math.radians(45)
        self.SCENE.objects.active = profile
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(+side, 0, 0), "constraint_orientation":'GLOBAL', "mirror":True, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, +side, 0), "constraint_orientation":'GLOBAL', "mirror":True, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.mirror(constraint_axis=(False, True, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(-side, 0, 0), "constraint_orientation":'GLOBAL', "mirror":True, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.mirror(constraint_axis=(True, False, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, -side, 0), "constraint_orientation":'GLOBAL', "mirror":True, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.transform.mirror(constraint_axis=(False, True, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.object.mode_set(mode='OBJECT')
        return profile

    def render(self):
        for i in range(0, 3):
            frame = self.spawn_frame(self.build_segment((-10, -10, i),  random.choice(self.FUNCTIONS), length = 3, pitch = 1.5), side = 20)
            self.assign_material(frame, self.random_material())
