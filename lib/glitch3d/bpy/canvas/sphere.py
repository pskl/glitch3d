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
    # Animation variables.
    currframe = 0
    fcount = 10
    invfcount = 1.0 / (fcount - 1)
    frange = bpy.context.scene.frame_end - bpy.context.scene.frame_start
    if frange == 0:
        bpy.context.scene.frame_end = 150
        bpy.context.scene.frame_start = 0
        frange = 150
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
                fprc = f * invfcount
                osc = abs(sin(TWOPI * fprc))
                bpy.context.scene.frame_set(currframe)
                # Animate location.
                self.vecrotate(TWOPI * fprc, axis, pt, rotpt)
                center = startcenter.lerp(stopcenter, osc)
                rotpt = rotpt + center
                current.location = rotpt
                current.keyframe_insert(data_path='location')
                # Animate rotation.
                currot = startrot.slerp(stoprot, jprc * fprc)
                current.rotation_euler = currot.to_euler()
                current.keyframe_insert(data_path='rotation_euler')
                # Animate color.
                mat.diffuse_color = colorsys.hsv_to_rgb(jprc, osc, 1.0)
                mat.keyframe_insert(data_path='diffuse_color')
                currframe += fincr

  def vecrotate(self, angle, axis, vin, vout):
    # Assume axis is a unit vector.
    # Find squares of each axis component.
    xsq = axis.x * axis.x
    ysq = axis.y * axis.y
    zsq = axis.z * axis.z
    cosa = cos(angle)
    sina = sin(angle)
    complcos = 1.0 - cosa
    complxy = complcos * axis.x * axis.y
    complxz = complcos * axis.x * axis.z
    complyz = complcos * axis.y * axis.z
    sinx = sina * axis.x
    siny = sina * axis.y
    sinz = sina * axis.z
    # Construct the x-axis (i).
    ix = complcos * xsq + cosa
    iy = complxy + sinz
    iz = complxz - siny
    # Construct the y-axis (j).
    jx = complxy - sinz
    jy = complcos * ysq + cosa
    jz = complyz + sinx
    # Construct the z-axis (k).
    kx = complxz + siny
    ky = complyz - sinx
    kz = complcos * zsq + cosa
    vout.x = ix * vin.x + jx * vin.y + kx * vin.z
    vout.y = iy * vin.x + jy * vin.y + ky * vin.z
    vout.z = iz * vin.x + jz * vin.y + kz * vin.z
    return vout

  def vecrotatex(self, angle, vin, vout):
    cosa = cos(angle)
    sina = sin(angle)
    vout.x = vin.x
    vout.y = cosa * vin.y - sina * vin.z
    vout.z = cosa * vin.z + sina * vin.y
    return vout