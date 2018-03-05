import uuid, sys, code, random, os, math, bpy

sys.path.append(os.path.dirname(__file__) + '/canvas.py')
canvas = __import__('canvas')

class Dreamatorium(canvas.Canvas):
    def render(self):
        bpy.ops.import_scene.obj(filepath = os.path.join(self.FIXTURES_FOLDER_PATH + 'm4a1.obj'), use_edges=True)
        bpy.ops.import_scene.obj(filepath = os.path.join(self.FIXTURES_FOLDER_PATH + 'lightning.obj'), use_edges=True)
        m4a1 = bpy.data.objects['m4a1']
        logo = bpy.data.objects["0_glitch3d_lightning"]
        logo.name = 'logo'
        logo.location = self.rand_location()
        m4a1.location = self.rand_location()
        m4a1.scale = (0.5, 0.5, 0.5)
        self.props.append(m4a1)
        self.props.append(logo)

        rand_primitive = random.choice(self.PRIMITIVES)
        elements = self.build_composite_object(rand_primitive, 4, 1)

        for l1 in elements:
            for l2 in l1:
                for obj in l2:
                    self.WIREFRAMES.append(obj)

        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
        display1 = self.last_added_object('Grid')
        display1.name = 'display_1'
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
        display2 = self.last_added_object('Grid')
        display2.name = 'display_2'

        bpy.data.groups['displays'].objects.link(display1)
        bpy.data.groups['displays'].objects.link(display2)

        display1.rotation_euler.x += math.radians(90)
        display1.rotation_euler.z -= math.radians(90)
        display2.rotation_euler.x += math.radians(90)
        display2.rotation_euler.y += math.radians(90)
        display2.rotation_euler.z += math.radians(120)

        for display in bpy.data.groups['displays'].objects:
            display.rotation_euler.x += math.radians(90)
            display.scale = self.DISPLAY_SCALE
            self.texture_object(display)
            self.unwrap_model(display)

        for prop in self.props:
            self.assign_material(prop, self.random_material())

        bpy.ops.mesh.primitive_plane_add(location=(0, 0, -2))
        floor = self.last_added_object('Plane')
        floor.name = 'floor'
        floor.scale = (20,20,20)
        self.subdivide(floor, int(random.uniform(1, 5)))
        self.displace(floor)

        self.OCEAN = self.add_ocean(10, 20)

        self.LINES = bpy.data.groups['lines']
        for j in range(0, random.choice(range(5, 40))):
            for i in range(0, random.choice(range(5, 40))):
                new_line = self.create_line('line' + str(uuid.uuid1()), self.series(30, random.choice(self.FUNCTIONS), 0.3), 0.003, (j, -10, 2))
                bpy.data.groups['lines'].objects.link(new_line)
                new_line.location.z += i / 3
                self.props.append(new_line)

        self.spawn_text("PSKL")

        for index in range(1, 5):
            new_object = self.spawn_text()
            bpy.data.groups['texts'].objects.link(new_object)
            self.props.append(new_object)
            text_scale = random.uniform(0.75, 3)
            self.assign_material(new_object, self.random_material())
            new_object.scale = (text_scale, text_scale, text_scale)
            new_object.location = self.rand_location()

        for obj in self.WIREFRAMES:
            self.wireframize(obj)