# Animate a metaball which is a collection of meta elements
import sys, code, random, os, math, bpy, canvas, colorsys
from math import pi, sin, cos, ceil
from mathutils import Vector, Quaternion
from random import TWOPI

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Metaballs(canvas.Canvas):

  TYPES =  ['BALL', 'CAPSULE', 'PLANE', 'ELLIPSOID', 'CUBE']

  def render(self):
    return None
    diameter = 8.0
    sz = 2.125 / diameter
    latitude = 16
    longitude = latitude * 2
    invlatitude = 1.0 / (latitude - 1)
    current_frame = 0
    jprc = 0.0
    phi = 0.0
    theta = 0.0
    pt = Vector((0.0, 0.0, 0.0))
    rotpt = Vector((0.0, 0.0, 0.0))
    center = Vector((0.0, 0.0, 0.0))
    baseaxis = Vector((0.0, 1.0, 0.0))
    axis = Vector((0.0, 0.0, 0.0))
    metaball_type = random.choice(self.TYPES)
    mbdata = bpy.data.metaballs.new('SphereData')
    mbdata.render_resolution = 0.075
    mbdata.resolution = 0.1
    mbobj = bpy.data.objects.new("Sphere", mbdata)
    bpy.context.scene.objects.link(mbobj)
    helpers.assign_material(mbobj, helpers.random_material(self.MATERIALS_NAMES))
    for i in range(0, latitude, 1):
        phi = pi * (i + 1) * invlatitude
        pt.z = cos(phi) * diameter
        for j in range(0, longitude, 1):
            theta = TWOPI * j / longitude
            pt.y = center.y + sin(phi) * sin(theta) * diameter
            pt.x = center.x + sin(phi) * cos(theta) * diameter
            mbelm = mbdata.elements.new(type=metaball_type)
            mbelm.co = (latitude, longitude, 6)
            mbelm.radius = 0.15 + sz * abs(sin(phi)) * 1.85
            mbelm.stiffness = 1.0
            if i % 7 == j % 3:
                mbelm.use_negative = True
            for f in range(0, self.NUMBER_OF_FRAMES, 1):
                fprc = f / (self.NUMBER_OF_FRAMES - 1)
                bpy.context.scene.frame_set(f)
                mbelm.co = helpers.rotate_vector(TWOPI * fprc, axis, pt)
                mbelm.keyframe_insert(data_path='co')
