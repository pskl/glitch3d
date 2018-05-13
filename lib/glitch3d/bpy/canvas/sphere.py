# Use noise to animate some objects in sphere pattern
import sys, code, random, os, math, bpy, canvas, colorsys
from math import pi, sin, cos, ceil
from mathutils import Vector, Quaternion
from random import TWOPI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Sphere(canvas.Canvas):
  def render(self):
    diameter = 8.0
    sz = 2.125 / diameter
    latitude = 16
    longitude = latitude * 2
    invlatitude = 1.0 / (latitude - 1)
    invlongitude = 1.0 / (longitude - 1)
    iprc = 0.0
    jprc = 0.0
    phi = 0.0
    theta = 0.0
    currframe = 0
    fcount = 10
    invfcount = 1.0 / (fcount - 1)
    frange = bpy.context.scene.frame_end - bpy.context.scene.frame_start
    fincr = ceil(frange * invfcount)
    # Animate center of the sphere.
    center = Vector((0.0, 0.0, 0.0))
    startcenter = Vector((0.0, -4.0, 0.0))
    stopcenter = Vector((0.0, 4.0, 0.0))
    # Rotate cubes around the surface of the sphere.
    pt = Vector((0.0, 0.0, 0.0))
    rotpt = Vector((0.0, 0.0, 0.0))
    # Change the axis of rotation for the point.
    baseaxis = Vector((0.0, 1.0, 0.0))
    axis = Vector((0.0, 0.0, 0.0))
    # Slerp between two rotations for each cube.
    startrot = Quaternion((0.0, 1.0, 0.0), pi)
    stoprot = Quaternion((1.0, 0.0, 0.0), pi * 1.5)
    currot = Quaternion()
    for i in range(0, latitude, 1):
        iprc = i * invlatitude
        phi = pi * (i + 1) * invlatitude
        sinphi = sin(phi)
        cosphi = cos(phi)
        rad = 0.01 + sz * abs(sinphi) * 0.99
        pt.z = cosphi * diameter
        for j in range(0, longitude, 1):
            jprc = j * invlongitude
            theta = TWOPI * j / longitude
            sintheta = sin(theta)
            costheta = cos(theta)
            pt.y = center.y + sinphi * sintheta * diameter
            pt.x = center.x + sinphi * costheta * diameter
            bpy.ops.mesh.primitive_cube_add(location=pt, radius=rad)
            current = bpy.context.object
            current.name = 'Cube ({0:0>2d}, {1:0>2d})'.format(i, j)
            current.data.name = 'Mesh ({0:0>2d}, {1:0>2d})'.format(i, j)
            current.rotation_euler = (0.0, phi, theta)
            # Append a material.
            mat = bpy.data.materials.new(name='Material ({0:0>2d}, {1:0>2d})'.format(i, j))
            mat.diffuse_color = colorsys.hsv_to_rgb(jprc, 1.0 - iprc, 1.0)
            current.data.materials.append(mat)
            # Append a bevel modifier to each cube for polish.
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers['Bevel'].segments = 2
            bpy.context.object.modifiers['Bevel'].width = 0.03
            self.vecrotatex(theta, baseaxis, axis)
            currframe = bpy.context.scene.frame_start
            currot = startrot
            center = startcenter
            for f in range(0, fcount, 1):
                fprc = f / (fcount - 1)
                osc = abs(sin(TWOPI * fprc))
                bpy.context.scene.frame_set(currframe)
                center = startcenter.lerp(stopcenter, osc)
                current.location = helpers.rotate_vector(TWOPI * fprc, axis, pt)
                current.keyframe_insert(data_path='location')
                currot = startrot.slerp(stoprot, jprc * fprc)
                current.rotation_euler = currot.to_euler()
                current.keyframe_insert(data_path='rotation_euler')
                mat.diffuse_color = colorsys.hsv_to_rgb(jprc, osc, 1.0)
                mat.keyframe_insert(data_path='diffuse_color')
                currframe += fincr

  def vecrotatex(self, angle, vin, vout):
    cosa = cos(angle)
    sina = sin(angle)
    vout.x = vin.x
    vout.y = cosa * vin.y - sina * vin.z
    vout.z = cosa * vin.z + sina * vin.y
    return vout