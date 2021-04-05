import bpy
import os
import importlib
import sys

if not os.path.dirname(os.path.abspath(__file__)) + "/../../modules" in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../modules")

import utils
import create_mesh

# main modules
import simple_subdivision
import catmull_clark_subdivision
import parameter_surfaces
import animation

importlib.reload( utils )
importlib.reload( create_mesh )

# main modules
importlib.reload( simple_subdivision )
importlib.reload( catmull_clark_subdivision )
importlib.reload( parameter_surfaces )
importlib.reload( animation )

# clear callbacks
bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_post.clear()

# execute
# argument 1: number of subdivisionssmooth 
# argument 2: smooth (True) or flat (False) shading.
animation.main(4, True)

# catmull_clark_subdivision.main()