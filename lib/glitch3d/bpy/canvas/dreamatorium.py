import uuid, sys, code, random, os, math, bpy, canvas, mathutils

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Dreamatorium(canvas.Canvas):
    def add_ocean(self, spatial_size, resolution, depth = 100, scale=(4,4,4), wave_scale = 0.5):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=1)
        ocean = helpers.last_added_object('Cube')
        ocean.scale = scale
        ocean.modifiers.new(name='Ocean', type='OCEAN')
        ocean.modifiers["Ocean"].spatial_size = spatial_size
        ocean.modifiers["Ocean"].resolution = resolution
        ocean.modifiers["Ocean"].wave_scale = wave_scale
        ocean.modifiers["Ocean"].depth = depth
        helpers.assign_material(ocean, helpers.fetch_material("jello"))
        shadow = helpers.duplicate_object(ocean)
        shadow.location += mathutils.Vector((1,1,-0.4))
        helpers.wireframize(shadow, random.choice(self.COLORS))
        shadow.name = 'shadow'
        ocean.name = 'ocean'
        return [ocean, shadow]

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
        # elements = helpers.build_composite_object(rand_primitive, 4, 1)

        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
        display1 = helpers.last_added_object('Grid')
        display1.name = 'display_1'
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
        display2 = helpers.last_added_object('Grid')
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
            helpers.texture_object(display, self.TEXTURE_FOLDER_PATH)
            helpers.unwrap_model(display)
            helpers.glitch(display)

        for prop in self.props:
            helpers.assign_material(prop, helpers.random_material(self.MATERIALS_NAMES))

        bpy.ops.mesh.primitive_plane_add(location=(0, 0, -2))
        floor = self.last_added_object('Plane')
        floor.name = 'floor'
        floor.scale = (20,20,20)
        helpers.subdivide(floor, int(random.uniform(1, 5)))
        helpers.displace(floor)

        self.OCEAN = self.add_ocean(10, 20)

        self.LINES = bpy.data.groups['lines']
        for j in range(0, random.choice(range(5, 40))):
            for i in range(0, random.choice(range(5, 40))):
                new_line = self.create_line('line' + str(uuid.uuid1()), self.series(30, self.rand_proba(self.FUNCTIONS), 0.3), random.choice(self.COLORS), 0.003, (j, -10, 2))
                bpy.data.groups['lines'].objects.link(new_line)
                new_line.location.z += i / 3
                self.props.append(new_line)

        helpers.spawn_text(self.TEXT_FILE_PATH, "PSKL")
        helpers.apply_displacement(bpy.data.objects['ocean'], self.HEIGHT_MAP_FOLDER_PATH)
        for index in range(1, 5):
            new_object = helpers.spawn_text(self.TEXT_FILE_PATH)
            bpy.data.groups['texts'].objects.link(new_object)
            self.props.append(new_object)
            text_scale = random.uniform(0.75, 3)
            self.assign_material(new_object, helpers.random_material(self.MATERIALS_NAMES))
            new_object.scale = (text_scale, text_scale, text_scale)
            new_object.location = helpers.rand_location()

        for obj in bpy.data.groups['neons'].objects:
            self.wireframize(obj, random.choice(self.COLORS))