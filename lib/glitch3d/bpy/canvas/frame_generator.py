# Generate a frame that you can 3D Print
# generate line -> rotate 45 degrees -> extrude -> mirror end -> cursor to center -> mirror
import uuid, math

def spawn_frame(segment, side = 40):
  profile = segment
  profile.name = 'Profile'
  profile.rotation_euler.z -= math.radians(45)
  bpy.data.scenes[-1].objects.active = profile
  bpy.ops.object.editmode_toggle()
  bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(+side, side, 0), "constraint_axis":(True, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
  bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(side, -side, 0), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
  # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(-side, -side, 0), "constraint_axis":(True, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
  # bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(-side, side, 0), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
  bpy.ops.object.mode_set(mode='OBJECT')
  # bpy.ops.mesh.remove_doubles()
  return profile

frame = spawn_frame(build_segment((0, 0, 0),  (lambda x: (0.5 * math.sin(0.5*x) + math.cos(x))), length = 2, pitch = 0.5), side = 20)
assign_material(frame, random_material())
apply_displacement(frame)

spawn_frame(build_segment((0, 1, 0),  (lambda x: (0.5 * math.sin(0.5*x) + math.cos(x))), length = 2, pitch = 0.5), side = 20)
spawn_frame(build_segment((0, 2, 0),  (lambda x: (0.5 * math.sin(0.5*x) * math.cos(x))), length = 2, pitch = 0.5), side = 20)
spawn_frame(build_segment((0, 3, 0),  (lambda x: (0.5 * math.sin(2*x) - math.cos(x))), length = 2, pitch = 0.5), side = 20)
spawn_frame(build_segment((0, 3, 0),  (lambda x: (0.5 * math.sin(2*x) - math.tan(x))), length = 2, pitch = 0.5), side = 20)