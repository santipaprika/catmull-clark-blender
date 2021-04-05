# Catmull-Clark surface subdivision algorithm implementation for Blender
Lab project for the advanced 3D modeling course in [MIRI](https://masters.fib.upc.edu/masters/miri-computer-graphics-and-virtual-reality), at UPC.
Implementation of the Catmull-clark surface subdivision algorithm for Blender, as a set of different functionallity modules (which may depend on each other).
The current implementation is robust to 2-manifold meshes, meshes with border edges, and meshes with crease edges at different intensities (which should be defined in the Blender editor).

## Output animation

https://user-images.githubusercontent.com/44426596/113601258-623ae680-9641-11eb-96ec-bc81b7036b4f.mp4



## How to set-up
The modules folder contains the python modules to be called from the script editor in Blender.  

In case of using the current repository structure, there is no need to add any path. Just load a blender scene (.blend) located
at the [models folder](models), open the file [blender-code-snippet.py](blender-code-snippet.py) in the script editor, and run (see [How to run](#how-to-run)).
  
Otherwise, you will need to append your [modules folder](modules) path (absolute or relative to the .blend file, as you prefer) to the system path, which
could be done in the loaded script in the blender script editor ([blender-code-snippet.py](blender-code-snippet.py)).

## How to run
To execute a specific module (once loaded the script [blender-code-snippet.py](blender-code-snippet.py) in the blender script editor) you only need to call its main function at the end of the [blender-code-snippet.py](blender-code-snippet.py) script (note that by default there is already a module call). E.g. if we want to execute the [parameter_surfaces.py](modules/parameter_surfaces.py) module, we should add:
```
parameter_surfaces.main(0.5, 3)
```
Some modules need input arguments (see [Modules](#modules))
  
## Modules
### simple_subdivision.py
Subdivides the selected mesh without applying any spatial modification.  
**Input arguments:** None  
**Example:**
```
simple_subdivision.main()
```

### catmull_clark_subdivision.py
Subdivides the selected mesh applying the catmull-clark surface subdivision algorithm.  
**Input arguments:** None  
**Example:**
```
catmull_clark_subdivision.main()
```

### parameter_surfaces.py
Subdivides the selected mesh applying both the simple and catmull-clark surface subdivision algorithms, and outputs an interpolated version between both.  
**Input arguments:** interpolation parameter (float), number of subdivisions to perform (int)  
**Example:**
```
parameter_surfaces.main(0.7, 3)
```

### animation.py
Subdivides the selected mesh applying both the simple and catmull-clark surface subdivision algorithms, and defines an animation callback that interpolates between both meshes
in terms of the current frame (dynamically). This option allows to render an animation of the whole interpolation process. There is an orbiting camera set-up by default.  
**Input arguments:** number of subdivisions to perform (int), use smooth shading (bool)  
**Example:**
```
animation.main(3, True)
```
