"""
File Name: PyImOGuizmo.py
Author: JuanMa Romero Martin <juanma@ihm.solutions>
Date Created:  2025-02-15
Last Modified: 2025-03-08
Description: This module provides functionalities for an interactive orientation 
             gizmo for ImGui in Python. It includes classes and functions to handle 
             camera movements, rotations, and view matrix generations, as well as 
             drawing and interacting with gizmo elements. 
             
TODO: 
    - Fix draw_gizmo()
    - Clean Up the code
    - Use quaternions for the rotations
    - Add option to setup the Y or Z axis as up vector. 
    - Add more customizations 
"""

from imgui_bundle import imgui, IM_COL32
import glm
import math


DEFAULT_POSITION = (0, 0, 10)
DEFAULT_YAW      = -90
DEFAULT_PITCH    = 0

DEFAULT_AXIS_UP      = glm.vec3( 0,  1,   0)
DEFAULT_AXIS_RIGHT   = glm.vec3( 1,  0,   0)
DEFAULT_AXIS_FORWARD = glm.vec3( 0,  0,  -1)

PITCH_MAX = 89.9 # degrees


class Camera:
    
    def __init__(self, aspect_ratio, position = DEFAULT_POSITION, yaw=DEFAULT_YAW, pitch=DEFAULT_PITCH):
        
                
        self.aspect_ratio = aspect_ratio
        
        self.position = glm.vec3(position)
        self.up       = DEFAULT_AXIS_UP
        self.right    = DEFAULT_AXIS_RIGHT
        self.forward  = DEFAULT_AXIS_FORWARD
        self._up      = glm.vec3( 0, 1, 0) # World Up Vector
        self.target   = glm.vec3( 0, 0, 0)
        
        self.yaw      = yaw
        self.pitch    = pitch

        self.FOV         = 60.0  # deg
        self.NEAR        = 0.1
        self.FAR         = 1000.0
        self.SPEED       = 0.005
        self.SENSITIVITY = 0.001 #0.04

        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
                
        
    def rotate(self, rel_x, rel_y):
        
        self.yaw   += rel_x * self.SENSITIVITY
        self.pitch -= rel_y * self.SENSITIVITY
        self.pitch  = max(-89, min(89, self.pitch))
        


    def update(self, delta_time): 
        self._velocity = self.SPEED * delta_time
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
        
        
    def update_camera_vectors(self):
        
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)
        yaw    = glm.radians(self.yaw) 
        pitch  = glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward) 
        self.right   = glm.normalize( glm.cross( self.forward, self._up ) )
        self.up      = glm.normalize( glm.cross( self.right, self.forward ) ) 
        
        
    def rotate_pich(self, delta_pitch):
        self.pitch -= delta_pitch
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)
        
        
    def rotate_yaw(self, delta_yaw):
            self.yaw +=delta_yaw
        
        
    def move_forward(self):
        self.position += self.forward * self._velocity
        
            
    def move_backward(self):
        self.position -= self.forward * self._velocity

    
    def move_right(self):
        self.position += self.right * self._velocity
    
    
    def move_left(self):
        self.position -= self.right * self._velocity


    def move_up(self):
        self.position += self.up * self._velocity
        
        
    def move_down(self):
        self.position -= self.up * self._velocity

    
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self._up)
        

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.FOV), self.aspect_ratio, self.NEAR, self.FAR)
        

    def get_distance(self):    
        return math.sqrt(   (self.position.x - self.target.x)**2 
                          + (self.position.y - self.target.y)**2 
                          + (self.position.z - self.target.z)**2 ) 
        
    
    def reset_model_view(self, position=DEFAULT_POSITION, pitch=DEFAULT_PITCH, yaw=DEFAULT_YAW):
        self.position = glm.vec3(position)
        self.up       = DEFAULT_AXIS_UP
        self.right    = DEFAULT_AXIS_RIGHT
        self.forward  = DEFAULT_AXIS_FORWARD
        self.yaw      = yaw
        self.pitch    = pitch
        


class GizmoConfig:
    def __init__(self):
        
        self.mDrawList:imgui.ImDrawList = None
        
        self.mX:float             = 0.0
        self.mY:float             = 0.0
        self.mSize:float          = 10.0
        self.pitch_rotation_speed:float = 0.005
        self.yaw_rotation_speed:float   = 0.002
        
        
        
        # In relation to half the rect size
        self.line_thickness_scale:float      = 0.017
        self.axis_length_scale:float         = 0.45 
        self.positive_radius_scale:float     = 0.12
        self.negative_radius_scale:float     = 0.085
        self.hover_circle_radius_scale:float = 0.77
        
        self.mColorWhite                     = IM_COL32( 255, 255, 255, 255)
        self.mColorBlack                     = IM_COL32(   0,   0,   0, 255)
        
        self.x_circle_front_color            = IM_COL32(255,  54,  83, 255)
        self.x_circle_back_color             = IM_COL32(255,  54,  83,  50)
        self.y_circle_front_color            = IM_COL32(138, 219,   0, 255)
        self.y_circle_back_color             = IM_COL32(138, 219,   0,  50)
        self.z_circle_front_color            = IM_COL32( 44, 143, 255, 255)
        self.z_circle_back_color             = IM_COL32( 44, 143, 255,  50)
        self.hover_circle_color              = IM_COL32(100, 100, 100, 130)
        

config = GizmoConfig()

              
def extract_vectors_from_view_matrix(view_matrix):
    """
    Extracts the right, up, and forward vectors from a view matrix.

    Args:
        view_matrix (glm.mat4): The view matrix.

    Returns:
        tuple: A tuple containing the right, up, and forward vectors as glm.vec3 objects.
    """
    
    right   = glm.vec3(view_matrix[0][0], view_matrix[1][0], view_matrix[2][0])
    up      = glm.vec3(view_matrix[0][1], view_matrix[1][1], view_matrix[2][1])
    forward = glm.vec3(view_matrix[0][2], view_matrix[1][2], view_matrix[2][2])
        
    # right   = glm.vec3(view_matrix[0][0], view_matrix[0][1], view_matrix[0][2])
    # up      = glm.vec3(view_matrix[1][0], view_matrix[1][1], view_matrix[1][2])
    # forward = glm.vec3(view_matrix[2][0], view_matrix[2][1], view_matrix[2][2])
    return right, up, forward


def compute_euler_angles_from_view_matrix(view_matrix):
    """
    Computes the Euler angles (yaw, pitch, roll) from a view matrix.

    Args:
        view_matrix (glm.mat4): The view matrix.

    Returns:
        tuple: A tuple containing the Euler angles (yaw, pitch, roll) in radians.
    """
    
    right, up, forward = extract_vectors_from_view_matrix(view_matrix)

    sy = math.sqrt(forward.x**2 + forward.z**2)
    
    if sy >1e-4: #1e-6:
        yaw   = math.atan2(forward.z, forward.x)
        pitch = math.atan2(-forward.y, sy)
        roll  = math.atan2(up.y, up.x)
    else: 
        yaw = math.atan2(-up.z, up.x)
        pitch = math.atan2(-forward.y, sy)
        roll = 0
    
    return yaw, pitch, roll
    
    
def color_change_opacity(color, opacity:float):
    
    color_float = imgui.color_convert_u32_to_float4(color)
    return IM_COL32(int(color_float.x * 255), 
                    int(color_float.y * 255), 
                    int(color_float.z * 255), 
                    int(opacity * 255) )


def check_inside_circle(center, radius, point):
    return (point.x - center.x) **2 + (point.y - center.y) **2 <= radius ** 2


def draw_positive_line(center, axis, color, radius, thickness, text, selected):
    
    line_end_positive = (center + axis).to_tuple()
    
    if math.isnan( line_end_positive[0] ) :
        return
    
    config.mDrawList.add_line( (center.x, center.y), line_end_positive, color, thickness)
    config.mDrawList.add_circle_filled(line_end_positive, radius, color)
    
    labelSize = imgui.calc_text_size(text)
    
    # text_pos = glm.vec2(line_end_positive[0] - 3.0, line_end_positive[1] - 6.0)
    text_pos = glm.vec2(math.floor(line_end_positive[0] - 0.5 * labelSize.x),
                        math.floor(line_end_positive[1] - 0.5 * labelSize.y)) 
            
    if selected:
        # config.mDrawList.add_circle(line_end_positive, radius, config.mColorWhite, 0, 1.1)
        config.mDrawList.add_text((text_pos.x, text_pos.y), config.mColorWhite, text)
    else:
        config.mDrawList.add_text( (text_pos.x, text_pos.y), config.mColorBlack, text)


def draw_negative_line(center, axis, color, radius, text, selected):
    
    line_end_negative = center - axis
    
    if math.isnan( line_end_negative[0] ) :
        return
    
    config.mDrawList.add_circle_filled((line_end_negative.x, line_end_negative.y) , radius, color_change_opacity(color, 0.3))
    config.mDrawList.add_circle((line_end_negative.x, line_end_negative.y), radius, color, 0, 1.1)
    
    labelSize = imgui.calc_text_size(text)
    text_pos  = glm.vec2(math.floor(line_end_negative[0] - 0.5 * labelSize.x),
                         math.floor(line_end_negative[1] - 0.35 * labelSize.y)) 
    
 
    
    if selected:
        config.mDrawList.add_circle((line_end_negative.x, line_end_negative.y), radius, config.mColorWhite, 0, 1.1)
        config.mDrawList.add_text(imgui.get_font(), 
                              13,
                              (text_pos.x, text_pos.y), 
                              config.mColorWhite, 
                              text)


def build_view_matrix(eye, at, up):
    
    # return glm.lookAtRH(eye, at, up) if right_handed else glm.lookAtLH(eye, at, up)
    return glm.lookAt(eye, at, up)
    

def set_rect(x, y, size):
    config.mX = x
    config.mY = y
    config.mSize = size


def set_draw_list(drawlist=None):
    config.mDrawList = drawlist if drawlist else imgui.get_window_draw_list()


def begin_frame(background=False):
    
    flags =   imgui.WindowFlags_.no_decoration \
            | imgui.WindowFlags_.no_inputs \
            | imgui.WindowFlags_.no_saved_settings \
            | imgui.WindowFlags_.no_focus_on_appearing \
            | imgui.WindowFlags_.no_bring_to_front_on_focus 
                
    if not background:
        flags |= imgui.WindowFlags_.no_background
    
    imgui.set_next_window_pos((config.mX, config.mY))
    imgui.set_next_window_size((config.mSize, config.mSize))
    imgui.begin("imoguizmo", None, flags)
    set_draw_list(config.mDrawList)
    imgui.end()


is_dragging_started:bool = False
last_mouse_pos:imgui.ImVec2Like = None


# Work In Progress
def draw_gizmo(view_matrix:glm.mat4, pivot_distance=0.0):
    
    global is_dragging_started
    
    size   = config.mSize
    h_size = size * 0.75
    center = glm.vec2(config.mX + h_size, config.mY + h_size)
    
    is_view_changed = False 
    is_dragging     = False
    is_hovered      = False
    
    delta_yaw   = 0
    delta_pitch = 0
    
    # view_projection = glm.transpose(view_matrix * glm.ortho(-1, 1, -1, 1, -1, 1) )
    # view_projection[1] *= -1
    view_projection = (view_matrix * glm.ortho(-1, 1, -1, 1, -1, 1) )
    # view_projection = (view_matrix * glm.perspective(10, 1, 0.2, 100) )
    view_projection[1] *= -1
    
    
    # Correction for non-square aspect ratio
    # aspect_ratio = projection_matrix[1, 1] / projection_matrix[0,0]
    # view_projection[0,0] *= aspect_ratio
    # view_projection[2,0] *= aspect_ratio

    # Axis
    axis_length = size * config.axis_length_scale
    # x_axis = multiply( glm.transpose(view_projection), glm.vec4(axis_length, 0, 0, 0))
    # y_axis = multiply( glm.transpose(view_projection), glm.vec4(0, axis_length, 0, 0))
    # z_axis = multiply( glm.transpose(view_projection), glm.vec4(0, 0, axis_length, 0))
    # z_axis *= -1
    
    # x_axis = multiply( (view_projection), glm.vec4(axis_length, 0, 0, 0))
    # y_axis = multiply( (view_projection), glm.vec4(0, axis_length, 0, 0))
    # z_axis = multiply( (view_projection), glm.vec4(0, 0, axis_length, 0))
    
    x_axis = view_projection * glm.vec4(axis_length, 0, 0, 0)
    y_axis = view_projection * glm.vec4(0, axis_length, 0, 0)
    z_axis = view_projection * glm.vec4(0, 0, axis_length, 0)
    z_axis *= -1
    
    
    interactive = pivot_distance > 0.0
    mouse_pos   = imgui.get_io().mouse_pos

    # Hover Circle
    hover_circle_radius = h_size * config.hover_circle_radius_scale
    set_draw_list(config.mDrawList)
    
    # 
    if check_inside_circle(center, hover_circle_radius, mouse_pos):
        is_hovered = True
    else: 
        is_hovered = False
    
    # 
    if interactive and is_hovered:
        config.mDrawList.add_circle_filled((center.x, center.y), hover_circle_radius, config.hover_circle_color)
        
    # 
    if is_hovered and imgui.is_mouse_down(imgui.MouseButton_.left) and not is_dragging_started:
        is_dragging_started = True
        is_dragging         = False


    if imgui.is_mouse_released(imgui.MouseButton_.left):
        is_dragging_started  = False
        is_dragging          = False

    
    if imgui.is_window_focused() and imgui.is_mouse_dragging(imgui.MouseButton_.left) and is_dragging_started:
        is_dragging = True
        
    
    # 
    positive_radius = size * config.positive_radius_scale
    negative_radius = size * config.negative_radius_scale
    
    # x_positive_closer = 0.0 <= x_axis.z
    # y_positive_closer = 0.0 <= y_axis.z
    # z_positive_closer = 0.0 <= z_axis.z

    x_positive_closer = 0.0 <= x_axis.z
    y_positive_closer = 0.0 <= y_axis.z
    z_positive_closer = 0.0 <= z_axis.z


    # Sort axis based on distance
	# 0 : -x axis, 1 : -y axis, 2 : -z axis, 3 : +x axis, 4 : +y axis, 5 : +z axis
    pairs = [(0, -x_axis.z), (1, -y_axis.z), (2, -z_axis.z), (3, x_axis.z), (4, y_axis.z), (5, z_axis.z)]
    # pairs = [(0, x_axis.w), (1, y_axis.w), (2, z_axis.w), (3, -x_axis.w), (4, -y_axis.w), (5, -z_axis.w)]
    
    pairs.sort(key=lambda x: x[1], reverse=True)

    selection = -1
    if not is_dragging:
        for pair in reversed(pairs):
            if selection == -1 and interactive:
                if pair[0]   == 0 and check_inside_circle(center + glm.vec2(x_axis.x, x_axis.y), positive_radius, mouse_pos):
                    selection = 0
                elif pair[0] == 1 and check_inside_circle(center + glm.vec2(y_axis.x, y_axis.y), positive_radius, mouse_pos):
                    selection = 1
                elif pair[0] == 2 and check_inside_circle(center + glm.vec2(z_axis.x, z_axis.y), positive_radius, mouse_pos):
                    selection = 2
                elif pair[0] == 3 and check_inside_circle(center - glm.vec2(x_axis.x, x_axis.y), negative_radius, mouse_pos):
                    selection = 3
                elif pair[0] == 4 and check_inside_circle(center - glm.vec2(y_axis.x, y_axis.y), negative_radius, mouse_pos):
                    selection = 4
                elif pair[0] == 5 and check_inside_circle(center - glm.vec2(z_axis.x, z_axis.y), negative_radius, mouse_pos):
                    selection = 5


    #  Draw back first
    line_thickness = size * config.line_thickness_scale
    for pair in pairs:
        if pair[0] == 0:
            draw_positive_line(center, 
                               glm.vec2(x_axis.x, x_axis.y), 
                               config.x_circle_front_color if x_positive_closer else config.x_circle_back_color, 
                               positive_radius, 
                               line_thickness, 
                               "X", 
                               selection == 0)
        elif pair[0] == 1:
            draw_positive_line(center, 
                                glm.vec2(y_axis.x, y_axis.y), 
                                config.y_circle_front_color if y_positive_closer else config.y_circle_back_color, 
                                positive_radius, 
                                line_thickness, 
                                "Y", 
                                selection == 1)
        elif pair[0] == 2:
            draw_positive_line(center, 
                                glm.vec2(z_axis.x, z_axis.y), 
                                config.z_circle_front_color if z_positive_closer else config.z_circle_back_color, 
                                positive_radius, 
                                line_thickness,
                                "Z", 
                                selection == 2)
        elif pair[0] == 3:
            draw_negative_line(center, 
                                glm.vec2(x_axis.x, x_axis.y), 
                                config.x_circle_front_color if not x_positive_closer else config.x_circle_back_color,                                
                                negative_radius, 
                                "-X",
                                selection == 3)
        elif pair[0] == 4:
            draw_negative_line(center, 
                                glm.vec2(y_axis.x, y_axis.y), 
                                config.y_circle_front_color if not y_positive_closer else config.y_circle_back_color, 
                                negative_radius,
                                "-Y",
                                selection == 4)
        elif pair[0] == 5:
            draw_negative_line(center, 
                                glm.vec2(z_axis.x, z_axis.y), 
                                config.z_circle_front_color if not z_positive_closer else config.z_circle_back_color, 
                                negative_radius, 
                                "-Z",
                                selection == 5)

    config.mDrawList = None

    new_view_matrix = view_matrix
    
    # Process Rotation
    if selection==-1 and is_dragging:
        
        length      = pivot_distance if pivot_distance > 0 else 1
        referenceUP = glm.vec3(0, 1, 0)
        cam_target  = glm.vec3(0)
        
        delta_mouse = imgui.get_mouse_drag_delta(imgui.MouseButton_.left, 1)
        
        right, referenceUP, dir = extract_vectors_from_view_matrix( view_matrix )
        yaw, pitch, roll        = compute_euler_angles_from_view_matrix(view_matrix)
   
        PITCH_MAX   = glm.radians(89.8)
        delta_yaw   = glm.radians(delta_mouse.x * config.yaw_rotation_speed)
        delta_pitch = glm.radians(delta_mouse.y * config.pitch_rotation_speed)

        yaw   += delta_yaw
        pitch += delta_pitch
        pitch  = glm.clamp(pitch, -PITCH_MAX, PITCH_MAX)
            
        direction = glm.vec3(
            glm.cos(yaw) * glm.cos(pitch),
            glm.sin(pitch),
            glm.sin(yaw) * glm.cos(pitch)
        )
        forward  = glm.normalize(direction)
        right    = glm.normalize(glm.cross(forward, referenceUP))
        up       = glm.normalize(glm.cross(right, forward))
        position = cam_target - forward * length
        
        new_view_matrix = glm.lookAt(position, position + forward, up )
        
        is_view_changed = True
        
     
    # Process Predefined Views
    if selection != -1 and imgui.is_mouse_clicked(imgui.MouseButton_.left):
        
        model_mat = glm.inverse(view_matrix)
        pivot_pos = glm.vec3(model_mat[3,0], model_mat[3,1], model_mat[3,2]) - glm.vec3(model_mat[2,0], model_mat[2,1], model_mat[2,2] ) * pivot_distance

        if selection == 0:
            new_view_matrix = build_view_matrix(pivot_pos + glm.vec3(pivot_distance, 0, 0), pivot_pos, glm.vec3(0, 1, 0))
        elif selection == 1:
            new_view_matrix = build_view_matrix(pivot_pos + glm.vec3(0, pivot_distance, 0), pivot_pos, glm.vec3(0, 0, -1))            
        elif selection == 2:
            new_view_matrix = build_view_matrix(pivot_pos + glm.vec3(0, 0, pivot_distance), pivot_pos, glm.vec3(0, 1, 0))
        elif selection == 3:
            new_view_matrix = build_view_matrix(pivot_pos - glm.vec3(pivot_distance, 0, 0), pivot_pos, glm.vec3(0, 1, 0))
        elif selection == 4:
            new_view_matrix = build_view_matrix(pivot_pos - glm.vec3(0, pivot_distance, 0), pivot_pos, glm.vec3(0, 0, 1))
        elif selection == 5:
            new_view_matrix = build_view_matrix(pivot_pos - glm.vec3(0, 0, pivot_distance), pivot_pos, glm.vec3(0, 1, 0))
        print(selection)
        is_dragging     = False
        is_view_changed = True
        selection       = -1   
    
    
    # Return the view matrix, and flags
    return is_view_changed, new_view_matrix, is_hovered, is_dragging



def draw_gizmo_camera(camera:Camera, interactive:bool=True):
    """_summary_

    Args:
        camera (Camera): _description_
        interactive (bool, optional): _description_. Defaults to True.
    """
    
    global is_dragging_started
    global last_mouse_pos
    
    size   = config.mSize
    h_size = size * 0.75
    center = glm.vec2(config.mX + h_size, config.mY + h_size)
    
    is_view_changed = False 
    is_dragging     = False
    is_hovered      = False
    
    delta_yaw   = 0
    delta_pitch = 0
    
    view_projection = camera.get_view_matrix() * glm.ortho(-1, 1, -1, 1, -1, 1) 
    

    # Axis
    axis_length = size * config.axis_length_scale        
    x_axis = view_projection * glm.vec4(axis_length, 0, 0, 0)
    y_axis = view_projection * glm.vec4(0, axis_length, 0, 0)
    z_axis = view_projection * glm.vec4(0, 0, axis_length, 0)
    z_axis *= -1
    
    
    mouse_pos   = imgui.get_io().mouse_pos

    # Hover Circle
    hover_circle_radius = h_size * config.hover_circle_radius_scale
    set_draw_list(config.mDrawList)
    
    # 
    if check_inside_circle(center, hover_circle_radius, mouse_pos):
        is_hovered = True
    else: 
        is_hovered = False
    
    # 
    if interactive and is_hovered:
        config.mDrawList.add_circle_filled((center.x, center.y), hover_circle_radius, config.hover_circle_color)
        
    # 
    if is_hovered and imgui.is_mouse_down(imgui.MouseButton_.left) and not is_dragging_started:
        is_dragging_started = True
        is_dragging         = False
        last_mouse_pos = imgui.get_mouse_pos()


    if imgui.is_mouse_released(imgui.MouseButton_.left):
        is_dragging_started  = False
        is_dragging          = False
        last_mouse_pos       = None

    
    if imgui.is_window_focused() and imgui.is_mouse_dragging(imgui.MouseButton_.left) and is_dragging_started:
        is_dragging = True
        
    
    # 
    positive_radius = size * config.positive_radius_scale
    negative_radius = size * config.negative_radius_scale
    
    x_positive_closer = 0.0 <= x_axis.z
    y_positive_closer = 0.0 <= y_axis.z
    z_positive_closer = 0.0 <= z_axis.z


    # Sort axis based on distance
	# 0 : -x axis, 1 : -y axis, 2 : -z axis, 3 : +x axis, 4 : +y axis, 5 : +z axis
    pairs = [(0, -x_axis.z), (1, -y_axis.z), (2, -z_axis.z), (3, x_axis.z), (4, y_axis.z), (5, z_axis.z)]
    pairs.sort(key=lambda x: x[1], reverse=True)

    selection = -1
    if not is_dragging:
        for pair in reversed(pairs):
            if selection == -1 and interactive:
                if pair[0]   == 0 and check_inside_circle(center + glm.vec2(x_axis.x, -x_axis.y), positive_radius, mouse_pos):
                    selection = 0
                elif pair[0] == 1 and check_inside_circle(center + glm.vec2(y_axis.x, -y_axis.y), positive_radius, mouse_pos):
                    selection = 1
                elif pair[0] == 2 and check_inside_circle(center + glm.vec2(z_axis.x, -z_axis.y), positive_radius, mouse_pos):
                    selection = 2
                elif pair[0] == 3 and check_inside_circle(center + glm.vec2(-x_axis.x, x_axis.y), negative_radius, mouse_pos):
                    selection = 3
                elif pair[0] == 4 and check_inside_circle(center + glm.vec2(-y_axis.x, y_axis.y), negative_radius, mouse_pos):
                    selection = 4
                elif pair[0] == 5 and check_inside_circle(center + glm.vec2(-z_axis.x, z_axis.y), negative_radius, mouse_pos):
                    selection = 5


    #  Draw back first
    line_thickness = size * config.line_thickness_scale
    for pair in pairs:
        if pair[0] == 0:
            draw_positive_line(center, 
                               glm.vec2(x_axis.x, -x_axis.y), 
                               config.x_circle_front_color if x_positive_closer else config.x_circle_back_color, 
                               positive_radius, 
                               line_thickness, 
                               "X", 
                               selection == 0)
        elif pair[0] == 1:
            draw_positive_line(center, 
                                glm.vec2(y_axis.x, -y_axis.y), 
                                config.y_circle_front_color if y_positive_closer else config.y_circle_back_color, 
                                positive_radius, 
                                line_thickness, 
                                "Y", 
                                selection == 1)
        elif pair[0] == 2:
            draw_positive_line(center, 
                                glm.vec2(z_axis.x, -z_axis.y), 
                                config.z_circle_front_color if z_positive_closer else config.z_circle_back_color, 
                                positive_radius, 
                                line_thickness,
                                "Z", 
                                selection == 2)
        elif pair[0] == 3:
            draw_negative_line(center, 
                                glm.vec2(x_axis.x, -x_axis.y), 
                                config.x_circle_front_color if not x_positive_closer else config.x_circle_back_color,                                
                                negative_radius, 
                                "-X",
                                selection == 3)
        elif pair[0] == 4:
            draw_negative_line(center, 
                                glm.vec2(y_axis.x, -y_axis.y), 
                                config.y_circle_front_color if not y_positive_closer else config.y_circle_back_color, 
                                negative_radius,
                                "-Y",
                                selection == 4)
        elif pair[0] == 5:
            draw_negative_line(center, 
                                glm.vec2(z_axis.x, -z_axis.y), 
                                config.z_circle_front_color if not z_positive_closer else config.z_circle_back_color, 
                                negative_radius, 
                                "-Z",
                                selection == 5)

    config.mDrawList = None

    delta = None
    
    # Process Rotation
    if selection==-1 and is_dragging and last_mouse_pos:
        
        mouse_pos = imgui.get_mouse_pos()
        delta = mouse_pos - last_mouse_pos
        last_mouse_pos = mouse_pos

        delta_yaw   = delta.x * config.yaw_rotation_speed
        delta_pitch = delta.y * config.pitch_rotation_speed
        
        PITCH_MAX = 89.9
        camera.yaw   += delta_yaw
        camera.pitch -= delta_pitch
        camera.pitch  = glm.clamp(camera.pitch, -PITCH_MAX, PITCH_MAX)
    
        yaw   = glm.radians(camera.yaw)
        pitch = glm.radians(camera.pitch)
        
        direction = glm.vec3(
            glm.cos(yaw) * glm.cos(pitch),
            glm.sin(pitch),
            glm.sin(yaw) * glm.cos(pitch)
        )
        camera.forward  = glm.normalize(direction)
        camera.right    = glm.normalize(glm.cross(camera.forward, camera.up))
        camera.up       = glm.normalize(glm.cross(camera.right, camera.forward))
        camera.position = camera.target - camera.forward * camera.get_distance()

        is_view_changed = True
        
        
     
    # Process Predefined Views
    if selection != -1 and imgui.is_mouse_clicked(imgui.MouseButton_.left):
        
        if selection == 0:   # X            
            camera.pitch = 0
            camera.yaw   = 180
        elif selection == 1: # Y            
            camera.pitch = 89.9
            camera.yaw   = 0           
        elif selection == 2: # Z            
            camera.pitch = 0
            camera.yaw   = 90
        elif selection == 3: # -X            
            camera.pitch = 0
            camera.yaw   = 0
        elif selection == 4: # -Y            
            camera.pitch = -89.9
            camera.yaw   = 0
        elif selection == 5: # -Z            
            camera.pitch = 0
            camera.yaw   = -90
            
        yaw   = glm.radians(camera.yaw)
        pitch = glm.radians(camera.pitch)
        
        direction = glm.vec3(
            glm.cos(yaw) * glm.cos(pitch),
            glm.sin(pitch),
            glm.sin(yaw) * glm.cos(pitch)
        )
        camera.forward  = glm.normalize(direction)
        camera.right    = glm.normalize(glm.cross(camera.forward, camera.up))
        camera.up       = glm.normalize(glm.cross(camera.right, camera.forward))
        camera.position = camera.target - camera.forward * camera.get_distance()
        
        is_dragging     = False
        is_view_changed = True
        selection       = -1   
    
    
    # Return the view matrix, and flags
    return is_view_changed, is_hovered, is_dragging