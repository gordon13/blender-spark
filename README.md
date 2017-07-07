# SPritesheet and Animation Rendering toolKit (SPARK)

SPARK is a spritesheet rendering and animation addon for Blender.

The idea is to be able to manage, and automate the rendering of your spritesheets and animations.

## Requirements

Works on Blender 2.78. It hasn't been tested on any other version, but it should work on older versions too.

## Installation

You install it via the Blender addon manager, and then it can be found in the 3D view in the properties panel.

## How to use

To use it, you click the "Add animation" button. This adds a box with some fields in it. Here are the fields and what they are used for:
* Armature - Armature which we want to animate and render
* Animation - Action/Animation which we want apply to the armature for animating
* Camera - Camera that will be used for rendering
* Output location - Defines where the spritesheet/frames will be saved
* Start frame - Frame on which the animation starts
* End frame - Frame on which the animation ends
* FPS - Defines the framerate at which to render the animation

Once everything is setup, the next time you make a change to an animation, you can either render only the animation that was changed, or if changes were made to the model, render all of them at once.