import uuid, sys, code, random, os, math, bpy, canvas, mathutils

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Dreamatorium(canvas.Canvas):
    def render(self):
        props = []
        bpy.ops.import_scene.obj(filepath = os.path.join(self.MODELS_FOLDER_PATH + 'lightning.obj'), use_edges=True)
        logo = bpy.context.selected_objects[0]
        logo.location = helpers.rand_location(self.CANVAS_BOUNDARY)
        props.append(logo)

        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
        display1 = bpy.context.object
        display1.name = 'display_1'
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
        display2 = bpy.context.object
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

        for j in range(0, random.choice(range(5, 40))):
            for i in range(0, random.choice(range(5, 10))):
                new_line = self.create_line('line' + str(uuid.uuid1()), self.series(30, self.rand_proba(self.FUNCTIONS), 0.3), random.choice(self.COLORS), 0.003, (j, -10, 2))
                bpy.data.groups['lines'].objects.link(new_line)
                new_line.location.z += i / 3
                props.append(new_line)

        ocean = self.add_ocean(10, 20)

        for index in range(1, 5):
            new_object = helpers.spawn_text(self.TEXT_FILE_PATH)
            bpy.data.groups['texts'].objects.link(new_object)
            props.append(new_object)
            helpers.assign_material(new_object, helpers.random_material(self.MATERIALS_NAMES))
            text_scale = random.uniform(0.75, 3)
            new_object.scale = (text_scale, text_scale, text_scale)
            new_object.location = helpers.rand_location(self.CANVAS_BOUNDARY)
            props.append(new_object)

        for obj in bpy.data.groups['neons'].objects:
            self.wireframize(obj, random.choice(self.COLORS))

        for f in range(self.NUMBER_OF_FRAMES):
          bpy.context.scene.frame_set(f)
          for prop in props:
            helpers.shuffle(prop, self.CANVAS_BOUNDARY)
            helpers.assign_material(prop, helpers.random_material(self.MATERIALS_NAMES))

    def add_ocean(self, spatial_size, resolution, depth = 100, scale=(4,4,4), wave_scale = 0.5):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=1)
        ocean = bpy.context.object
        ocean.scale = scale
        ocean.modifiers.new(name='Ocean', type='OCEAN')
        ocean.modifiers["Ocean"].spatial_size = spatial_size
        ocean.modifiers["Ocean"].resolution = resolution
        ocean.modifiers["Ocean"].wave_scale = wave_scale
        ocean.modifiers["Ocean"].depth = depth
        helpers.wireframize(ocean, random.choice(self.COLORS))
        ocean.name = 'ocean'
        return ocean
