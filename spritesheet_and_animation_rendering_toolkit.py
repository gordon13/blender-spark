bl_info = {
    "name": "SPARK: Spritesheet and Animation Rendering Toolkit",
    "description": "SPARK (SPritesheet and Animation Rendering toolKit) allows the user to automate the rendering of their animations. The tool saves frame rate, start and end frames, cameras and more. Updating all animation renders is then just one click away.",
    "author": "Paul Le Henaff",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "category": "Rendering",
}

import bpy
import numpy as np
import glob
import math
import os
from bpy.types import Header, Menu, Panel

class VIEW3D_PT_sprite_animation(Panel):
    """
    SPARK: SPritesheet and Animation Rendering Toolkit
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "SPARK"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        view = context.space_data

    def draw(self, context):
        layout = self.layout

        view = context.space_data
        use_multiview = context.scene.render.use_multiview

        col = layout.column()
        sub = col.row()
        sub.operator("spritesheet_generator.addanimation")
        sub.operator("spritesheet_generator.generateallspritesheet", text="Render all animations", icon="RENDER_STILL")
        
        col = layout.column()
        for i, anim in enumerate(bpy.context.scene.animationsToRender):
            box = layout.box()
            row = box.row(align=True)
            
            # header for each animation box
            row.prop(anim, "show_expanded", icon="TRIA_DOWN" if anim.show_expanded else "TRIA_RIGHT", text="", emboss=False)
            row.prop(anim, "active", text="")
            if anim.animation != "":
                row.label(text=anim.animation)
            else:
                row.label(text="Not Set")
            row.operator("spritesheet_generator.removeanimation", text="", emboss=False, icon='X').index = i

            # body of animation box
            if (anim.show_expanded):
                row = box.row()
                row.prop(anim, "armature", text="")
                row.prop(anim, "animation", text="")
                row = box.row()
                row.prop(anim, "camera", text="Camera")
                row = box.row()
                row.prop(anim, "output_path", text="Output location")
                row = box.row()
                row.prop(anim, "start_frame", text="Start frame")
                row.prop(anim, "end_frame", text="End frame")
                row = box.row()
                row.prop(anim, "fps", text="FPS")
                row.operator("spritesheet_generator.rendesingleanimationframes", icon="RENDER_STILL").index = i
                row = box.row()
                row.prop(anim, "spritesheet_output_path", text="Spritesheet output location")
                row = box.row()
                row.operator("spritesheet_generator.generatesinglespritesheet").index = i

# =====================================================
#                       FUNCTIONS
# =====================================================
def load_image(file_path):
    try:
        return bpy.data.images.load(file_path)
    except:
        raise NameError("Cannot load image %s" % file_path)

def roundToPowerOf2(inputToRoundUp):
    inputToRoundUp = int(inputToRoundUp)
    inputToRoundUp -= 1
    inputToRoundUp |= inputToRoundUp >> 1
    inputToRoundUp |= inputToRoundUp >> 2
    inputToRoundUp |= inputToRoundUp >> 4
    inputToRoundUp |= inputToRoundUp >> 8
    inputToRoundUp |= inputToRoundUp >> 16
    inputToRoundUp += 1
    return inputToRoundUp

def get_max_num_sprites(image_names):
    size = len(image_names)
    return ( int(size / 2), int(size / 2) ) if size % 2 == 0 else ( int((size - 1) / 2), int(((size - 1) / 2) + 1) )

def place(sub_image, new_image, x, y):
    """
    this function updates the new_image "in place"
    """ 
    new_image_pixels_1d = np.array(new_image.pixels)
    print(new_image_pixels_1d.size)
    
    new_image_pixels_2d = np.reshape(new_image_pixels_1d, (new_image.size[1], new_image.size[0] * 4))
    print(new_image_pixels_2d.size)
    
    sub_image_pixels_2d = np.reshape(np.array(sub_image.pixels), (sub_image.size[1], sub_image.size[0]*4))
    print(new_image_pixels_2d.size)
    
    print("(", new_image.size[1], " -", y, ") - ", sub_image.size[1])
    sub_image_width = sub_image.size[0]
    sub_image_height = sub_image.size[1]
    y = (new_image.size[1] - y) - sub_image_height # convert y position to opengl space
    x *= 4 # scale x value by the number of channels because the array is wider in the x axis than the y axis by this much
    
    print("converted position x:", x, ", y:", y)
    
    new_image_pixels_2d[ y : y + sub_image_height, x : x + (sub_image_width * 4) ] = sub_image_pixels_2d
    new_image.pixels = new_image_pixels_2d.flatten()


# =====================================================
#                       PROPERTIES
# =====================================================
def getArmatures(self, context):
    armatures = []
    for object in context.scene.objects:
        if object.type == "ARMATURE":
            armatures.append(object)
    return [(armature.name, armature.name, armature.name) for armature in armatures]

def getActions(self, context):
    return [ (action.name, action.name, action.name) for action in bpy.data.actions ]

def getCameras(self, context):
    cameras = []
    for object in context.scene.objects:
        if object.type == "CAMERA":
            cameras.append(object)
    return [(cam.name, cam.name, cam.name) for cam in cameras]


class customPropertiesGroup(bpy.types.PropertyGroup):
    active = bpy.props.BoolProperty(default=True)
    show_expanded = bpy.props.BoolProperty(default=True)
    armature = bpy.props.EnumProperty(items = getArmatures)
    camera = bpy.props.EnumProperty(items = getCameras)
    animation = bpy.props.EnumProperty(items = getActions)
    output_path = bpy.props.StringProperty(default="//", maxlen=1024, subtype='FILE_PATH')
    start_frame = bpy.props.IntProperty()
    end_frame = bpy.props.IntProperty()
    fps = bpy.props.IntProperty(default=24)
    spritesheet_output_path = bpy.props.StringProperty(default="//", maxlen=1024, subtype='FILE_PATH')



# =====================================================
#                       OPERATORS
# =====================================================
class AddAnimationButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.addanimation"
    bl_label = "Add animation"
    def execute(self, context):
        bpy.context.scene.animationsToRender.add()
        return{'FINISHED'}

class RemoveAnimationButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.removeanimation"
    bl_label = "Add animation"
    index = bpy.props.IntProperty()
    def execute(self, context):
        bpy.context.scene.animationsToRender.remove(self.index)
        return{'FINISHED'}

class RenderSingleAnimationFramesButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.rendesingleanimationframes"
    bl_label = "Render animation"
    index = bpy.props.IntProperty()
    def execute(self, context):
        selected_animation = bpy.context.scene.animationsToRender[self.index]
        if (selected_animation.active):
            animation_name = selected_animation.animation
            current_action = bpy.data.actions[animation_name]

            # setup active animation
            bpy.context.scene.objects[selected_animation.armature].animation_data.action = current_action

            # setup camera
            bpy.context.scene.camera = bpy.data.objects[selected_animation.camera]
            
            # setup frames
            bpy.context.scene.frame_start = selected_animation.start_frame
            bpy.context.scene.frame_end = selected_animation.end_frame
            bpy.context.scene.frame_set( 0 )

            # setup output location
            bpy.context.scene.render.filepath = selected_animation.output_path

            # render settings
            bpy.context.scene.cycles.film_transparent = True
            bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
            bpy.context.scene.render.fps = selected_animation.fps
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.image_settings.color_mode ='RGBA'

            # render animation
            bpy.ops.render.render({'dict': "override"}, 'INVOKE_DEFAULT', animation=True)

            # TODO: reset settings back to original

        return{'FINISHED'}


class GenerateSingleSpritesheetButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.generatesinglespritesheet"
    bl_label = "Generate spritesheet"
    index = bpy.props.IntProperty()
    def execute(self, context):
        selected_animation = bpy.context.scene.animationsToRender[self.index]
        if (selected_animation.active):
            formatted_path = bpy.path.abspath(selected_animation.output_path)
            path_parts = os.path.split(formatted_path)

            # get absolute path
            absolute_path = path_parts[0]

            # get name and format
            frame_name, frame_format = path_parts[1].split(".", 1)
            
            # get all images from the given path
            image_names = glob.glob("%s*.png"%os.path.join(absolute_path, ''))
            if (len(image_names) == 0):
                self.report({"ERROR"}, "No frames detected. You must render the animation first!")
                return {'CANCELLED'}

            # number of sprites in x and y direction (handles odd and even number )
            x_num_sprites, y_num_sprites = get_max_num_sprites(image_names)

            new_image = None
            last_x, last_y = (0,0)
            for name in image_names:
                print("--------")
                real_path = bpy.path.abspath('//' + name)
                image = load_image(real_path)

                if (new_image == None):

                    # calculate dimensions of spritesheet
                    max_x_size = x_num_sprites * image.size[0]
                    max_y_size = roundToPowerOf2(y_num_sprites * image.size[1]) # ensure dimensions is power of 2

                    # remove existing image otherwise we end up with image.0001, 0002 etc
                    spritesheet_name = "%s_spritesheet" % frame_name
                    spritesheet = bpy.data.images.get(spritesheet_name)
                    if (spritesheet is not None):
                        bpy.data.images.remove(spritesheet, do_unlink=True)

                    # create blank image based on dimensions we calculated earlier
                    new_image = bpy.data.images.new(spritesheet_name, max_x_size, max_y_size, True )

                if (last_x + image.size[0] > max_x_size):
                    last_x = 0
                    last_y += image.size[1]
                place(image, new_image, last_x, last_y)
                # if (last_x + image.size[0] <= max_x_size):
                #     place(image, new_image, last_x, last_y)
                # else:
                #     last_x = 0
                #     last_y += image.size[1]
                #     place(image, new_image, last_x, last_y)
                last_x += image.size[0]

            new_image.use_alpha = True
            new_image.alpha_mode = 'STRAIGHT'
            spritesheet_output_path = bpy.path.abspath(selected_animation.spritesheet_output_path)
            new_image.filepath_raw = spritesheet_output_path
            new_image.file_format = 'PNG'
            new_image.save()

            self.report({"INFO"}, "Spritesheet rendered at location %s"%spritesheet_output_path)

        return {'FINISHED'}


class GenerateAllSpritesheetButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.generateallspritesheet"
    bl_label = "Generate all spritesheets"
    def execute(self, context):
        for i, anim in enumerate(bpy.context.scene.animationsToRender):
            print(i)
            bpy.ops.spritesheet_generator.rendesingleanimationframes(i)
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.animationsToRender = bpy.props.CollectionProperty(type=customPropertiesGroup)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.animationsToRender

if __name__ == "__main__":
    register()