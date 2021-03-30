import bpy
import os
import importlib
import sys

if not os.path.dirname(os.path.abspath(__file__)) + "/../../modules" in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../modules")

import create_mesh
import simple_subdivision
import catmull_clark_subdivision
import parameter_surfaces
import animation

importlib.reload( create_mesh )
importlib.reload( simple_subdivision )
importlib.reload( catmull_clark_subdivision )
importlib.reload( parameter_surfaces )
importlib.reload( animation )

animation.main()
#simple_subdivision.main()
#filename = os.path.join(os.path.dirname(bpy.data.filepath), "../modules/simple_subdivision.py")
#exec(compile(open(filename).read(), filename, 'exec'))