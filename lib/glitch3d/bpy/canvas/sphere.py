# Use noise to animate some objects in sphere pattern
import sys, code, random, os, math, bpy, canvas, colorsys
from math import pi, sin, cos, ceil
from mathutils import Vector, Quaternion
from random import TWOPI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Sphere(canvas.Canvas):
  def render(self):
    diameter = 4.0
    sz = 2.125 / diameter
    base_object = helpers.infer_primitive(random.choice(self.PRIMITIVES), location = (100, 100, 100), radius=sz)
    latitude = 16
    longitude = latitude * 2
    invlatitude = 1.0 / (latitude - 1)
    invlongitude = 1.0 / (longitude - 1)
    iprc = 0.0
    jprc = 0.0
    phi = 0.0
    theta = 0.0
    invfcount = 1.0 / (self.NUMBER_OF_FRAMES - 1)
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
        rad = 0.01 + sz * abs(sin(phi)) * 0.99
        pt.z = cos(phi) * diameter
        for j in range(0, longitude, 1):
            jprc = j * invlongitude
            theta = TWOPI * j / longitude
            pt.y = center.y + sin(phi) * sin(theta) * diameter
            pt.x = center.x + sin(phi) * cos(theta) * diameter
            current = helpers.duplicate_object(base_object)
            current.location = pt
            current.name = 'Object ({0:0>2d}, {1:0>2d})'.format(i, j)
            current.data.name = 'Mesh ({0:0>2d}, {1:0>2d})'.format(i, j)
            current.rotation_euler = (0.0, phi, theta)
            helpers.assign_material(current, helpers.random_material(self.MATERIALS_NAMES))
            axis = self.vecrotatex(theta, baseaxis)
            currot = startrot
            center = startcenter
            for f in range(0, self.NUMBER_OF_FRAMES, 1):
                fprc = f / (self.NUMBER_OF_FRAMES - 1)
                osc = abs(sin(TWOPI * fprc))
                bpy.context.scene.frame_set(f)
                center = startcenter.lerp(stopcenter, osc)
                current.location = helpers.rotate_vector(TWOPI * fprc, axis, pt)
                current.keyframe_insert(data_path='location')
                currot = startrot.slerp(stoprot, jprc * fprc)
                current.rotation_euler = currot.to_euler()
                current.keyframe_insert(data_path='rotation_euler')

  # Rotate vector by a given angle from a starting vector and return a new vector
  # Trigonometry:
  #  x' = x cos θ − y sin θ
  #  y' = x sin θ + y cos θ
  def vecrotatex(self, angle, vin):
    vout = Vector((0.0, 0.0, 0.0))
    vout.x = vin.x
    vout.y = cos(angle) * vin.y - sin(angle) * vin.z
    vout.z = cos(angle) * vin.z + sin(angle) * vin.y
    return vout