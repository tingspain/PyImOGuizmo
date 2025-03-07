# PyImoGuizmo

### An Interactive Orientation Gizmo for ImGui in Python

> ⚠️ Warning This Library is still Work In Progress 🚧 👷 ‼️


<video controls>
<source src="media/PyImOGuizmo_Demo.mp4" type="video/mp4">
</video>

PyImoGuizmo is a Python library mostly ported from the C++ [ImOGuizmo library](https://github.com/fknfilewalker/imoguizmo). It provides an interactive orientation gizmo for the 3D Viewport  within ImGui-based applications, such as those using [imgui_bundle](https://github.com/pthom/imgui_bundle).

This library is designed to be simple and easy to integrate into your ImGui-based applications. PyImoGuizmo is based on PyGLM for efficient matrix operations and transformations.


### Features

- Interactive orientation gizmo for 3D transformations
- Configurable colors, axis length, and other properties
- Supports both left-handed and right-handed coordinate systems
- Easy to use with ImGui in Python
- Based on PyGLM for matrix operations

### Installation

Currently, you can install PyImoGuizmo by either:

* Downloading the PyImoGuizmo.py file directly.
* Cloning this repository.

A PyPI release is planned once the library reaches a more stable and mature state.



### Usage

Here's a basic example of how to use PyImoGuizmo in your project:

```Python
from imgui_bundle import imgui
import glm  # PyGLM for matrix operations
import PyImOGuizmo 

# Set Rotation Sensitivity per axis of rotation
PyImOGuizmo.config.yaw_rotation_speed   = 0.25 
PyImOGuizmo.config.pitch_rotation_speed = 0.25 


# Pass the draw list of the current window to the PyImOGuizmo
PyImOGuizmo.set_draw_list()

# Set the location of the Gizmo
PyImOGuizmo.set_rect( rect_max.x - 120, 
                      rect_min.y, 
                      80)

# PyImOGuizmo.begin_frame() 

# Draw the Gizmo
is_view_changed, is_gizmo_hovering, is_gizmo_draggig = PyImOGuizmo.draw_gizmo_camera(viewport_camera)


```

### Note

TBD


### Example

TBD

![Example App](media/PyImOGuizmo_Example_App.png)

### Roadmap

This library is still under development. The following tasks are on the roadmap:

TBD

### License

TBD
