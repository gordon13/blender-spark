bl_info = {
    "name": "SPARK: SPritesheet and Animation Rendering toolKit",
    "description": "SPARK allows the user to automate the rendering of their animations. The tool saves frame rate, start and end frames, cameras and more. Updating all animation renders is then just one click away.",
    "author": "Paul Le Henaff",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "category": "Rendering",
}

import bpy
import os
from bpy.types import Header, Menu, Panel

class VIEW3D_PT_sprite_animation(Panel):
    """
   
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "SPARTa"
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
                row.operator("spritesheet_generator.generatesinglespritesheet", icon="RENDER_STILL").index = i


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
    output_path = bpy.props.StringProperty(default="", maxlen=1024, subtype='FILE_PATH')
    start_frame = bpy.props.IntProperty()
    end_frame = bpy.props.IntProperty()
    fps = bpy.props.IntProperty(default=24)



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

class GenerateSingleSpritesheetButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.generatesinglespritesheet"
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
            bpy.context.scene.render.alpha_mode = 'TRANSPARENT' #
            bpy.context.scene.render.fps = selected_animation.fps
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.image_settings.color_mode ='RGBA'

            # render animation
            bpy.ops.render.render({'dict': "override"}, 'INVOKE_DEFAULT', animation=True)

            # TODO: reset settings back to original

        return{'FINISHED'}

class GenerateAllSpritesheetButton(bpy.types.Operator):
    bl_idname = "spritesheet_generator.generateallspritesheet"
    bl_label = "Generate all spritesheets"
    def execute(self, context):
        for i, anim in enumerate(bpy.context.scene.animationsToRender):
            print(i)
            bpy.ops.spritesheet_generator.generatesinglespritesheet(i)
        return{'FINISHED'}



def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.animationsToRender = bpy.props.CollectionProperty(type=customPropertiesGroup)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.animationsToRender

if __name__ == "__main__":
    register()