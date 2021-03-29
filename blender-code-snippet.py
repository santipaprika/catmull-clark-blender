import bpy
import os
import imp
import sys

if not os.path.dirname(os.path.abspath(__file__)) + "/../../modules" in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../modules")

import simple_subdivision
import catmull_clark_subdivision
import create_mesh

imp.reload( simple_subdivision )
imp.reload( create_mesh )
imp.reload( catmull_clark_subdivision )
catmull_clark_subdivision.main()
#simple_subdivision.main()
#filename = os.path.join(os.path.dirname(bpy.data.filepath), "../modules/simple_subdivision.py")
#exec(compile(open(filename).read(), filename, 'exec'))