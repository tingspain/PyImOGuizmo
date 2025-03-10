#!/usr/bin/env uv run
# -*- coding: utf-8 -*-

"""
File Name: main.py
Author: JuanMa Romero Martin <juanma@ihm.solutions>
Date Created:  2025-03-01
Last Modified: 2025-03-08
Description: This is a demo app to demonstrate how to use PyImOGuizmo and also 
             how to use ModernGL with ImGui Bundle.

TODO:  
    - Clean up the code
"""

import os.path
import sys
sys.path.append('..')

import platform
import OpenGL.GL as GL  # type: ignore
import moderngl
from imgui_bundle import imgui, immapp

from imgui_bundle import immapp as immapp, ImVec4
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome


# Always import glfw *after* imgui_bundle
# (since imgui_bundle will set the correct path where to look for the correct 
# version of the glfw dynamic library)
import glfw  # type: ignore

import numpy as np
import glm

try:
    from PIL import Image
except ImportError as ex:
    raise ImportError("Texture loader 'PillowLoader' requires Pillow: {}".format(ex))

# Import local Libraries
import mesh as Mesh
import PyImOGuizmo 



class AppState():
    
    def __init__(self):  
        self.show_imgui_demo: bool              = False
        self.use_imoguizmo_camera_version: bool = True
    
    
app_state = AppState()



def glfw_error_callback(error: int, description: str) -> None:
    """
    Handle GLFW errors.
    """
    sys.stderr.write(f"Glfw Error {error}: {description}\n")



def create_texture(ctx, path):
        image   = Image.open(path)
        image = image.transpose( Image.Transpose.FLIP_TOP_BOTTOM)

        texture = ctx.texture(size=image.size, components=3, data=image.convert("RGB").tobytes())
        
        # mipmaps
        texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        texture.build_mipmaps()
    
        # AF
        texture.anisotropy = 32.0
        return texture



def create_framebuffer(ctx, width, height):
    """
    Create a framebuffer object (FBO) using ModernGL.
    """
    color_texture = ctx.texture((width, height), 4)  # Create color attachment
    depth_buffer  = ctx.depth_renderbuffer((width, height))  # Create depth attachment
    fbo           = ctx.framebuffer(color_attachments=[color_texture], depth_attachment=depth_buffer)
    return fbo, color_texture



def create_main_menu():
    
    imgui.push_style_var(imgui.StyleVar_.window_padding, (6, 8))
    imgui.push_style_var(imgui.StyleVar_.frame_padding,  (6, 8))
    
    # Start the Main Menu 
    imgui.begin_main_menu_bar()


    if imgui.begin_menu("File"):
        
        clicked, _ = imgui.menu_item("New", "", False)
        if clicked:
            print("Executing New")
        
        clicked, _ = imgui.menu_item("Open", "", False)
        if clicked:
            print("Executing Open")
        
        clicked, _ = imgui.menu_item("Save", "", False)
        if clicked:
            print("Executing Save")
            
        imgui.separator()
        clicked, _ = imgui.menu_item("Exit", "", False)
        if clicked:
            exit(1)
        
        imgui.end_menu()
       
        
    if imgui.begin_menu("Edit"):
        
        clicked, _ = imgui.menu_item("Test me", "", False)
        if clicked:
            print("Testing you")
        
        imgui.end_menu()
      
      
    if imgui.begin_menu("Views"):
        
        clicked, _ = imgui.menu_item("Show/Hide Imgui Demo", "", False)
        if clicked:
            app_state.show_imgui_demo = not app_state.show_imgui_demo
        
        imgui.end_menu()
            
    imgui.end_main_menu_bar()
    
    imgui.pop_style_var(2)
        


def load_icon_fonts():
    
    # Load font example, with a merged font for icons
    # ------------------------------------------------
    # i. Load default font
    
    font_config = imgui.ImFontConfig()
    font_config.size_pixels = 14
    font_config.rasterizer_density = 2
    
    font_atlas = imgui.get_io().fonts
    font_atlas.add_font_default(font_config)
    
    this_dir = os.path.dirname(__file__)
    
    # # ii. ... And merge icons into the previous font

    font_filename = this_dir + "/assets/fonts/fontawesome-webfont.ttf"
    font_config = imgui.ImFontConfig()
    font_config.merge_mode = True
    font_config.rasterizer_multiply = 2.0 
    icon_size = 15

    icons_range = [icons_fontawesome.ICON_MIN_FA, icons_fontawesome.ICON_MAX_FA, 0]
    font_atlas.add_font_from_file_ttf(
        filename=font_filename,
        size_pixels = icon_size,
        glyph_ranges_as_int_list=icons_range,
        font_cfg=font_config,
    )
     
     

def display_overlay_extra_info(is_hovered, is_focused, cur_window_pos, camera_position):

    cursor_pos = cur_window_pos
    
    imgui.set_cursor_pos((20, 40))
    
    imgui.begin_group()
    
    imgui.text("Hovered:")
    imgui.same_line()
    if(is_hovered):
        imgui.text_colored((1.0, 1.105, 0.105, 1.00), "On")
    else: 
        imgui.text_colored((0.400, 0.400, 0.400, 1.00), "Off")
        
    imgui.text("Focused:")
    imgui.same_line()
    if(is_focused):
        imgui.text_colored((1.0, 1.105, 0.105, 1.00), "On")
    else: 
        imgui.text_colored((0.400, 0.400, 0.400, 1.00), "Off")
        
    imgui.text("Mouse X:")
    imgui.same_line()
    mouse_pos    = imgui.get_mouse_pos()
    viewport_pos = imgui.get_cursor_start_pos()
    if(is_hovered):
        imgui.text_colored((1.0, 1.105, 0.105, 1.00), str(  ( mouse_pos.x - cursor_pos.x - viewport_pos.x, mouse_pos.y - cursor_pos.y - viewport_pos.y)) )
    else: 
        imgui.text_colored((1.0, 1.105, 0.105, 1.00), "(Nan, Nan)" )
        
    imgui.end_group()


    
def LabelPrefix(label:str) -> str:
    """Prefixes the label of an ImGui widget and aligns it to the left position.

    This function adjusts the position of a given label in an ImGui interface to 
    the left side, and prefixes the label with '##' to create a unique label ID. 
    It first calculates the item width and the text line height with spacing, 
    then adjusts the cursor position to align the text to the frame padding. After 
    printing the label, it moves the cursor to the appropriate position for the
    next item and returns the prefixed label ID for further usage in ImGui widgets.

    Args:
        label (str): The label to be aligned, printed, and prefixed.

    Returns:
        str: A unique label ID generated by prefixing the input label with '##'.
    """
        
    width  = imgui.calc_item_width()
    height = imgui.get_text_line_height_with_spacing()
    
    x = imgui.get_cursor_pos_x()
    y = imgui.get_cursor_pos_y()
    imgui.align_text_to_frame_padding()
    imgui.text(label)
    imgui.same_line()
    imgui.set_cursor_pos_x(x + width  * 0.5 + imgui.get_style().item_inner_spacing.x)
    
    imgui.set_next_item_width(-1)
    
    labelID:str = "##"
    labelID += label
    
    return labelID

             
def main() -> None:
        
    # Setup window
    glfw.set_error_callback( glfw_error_callback )
    if not glfw.init():
        sys.exit(1)

    # Decide GL+GLSL versions
    if platform.system() == "Darwin":
        glsl_version = "#version 150"
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4) # 3
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1) # 2
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)  # // 3.2+ only
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE) 
    else:
        # GL 3.0 + GLSL 130
        glsl_version = "#version 130"
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE) # // 3.2+ only
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)

    # Create window with graphics context
    window = glfw.create_window(1200, 800, "PyImOGuizmo Example v0.0.1", None, None)
    if window is None:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

        
    glfw.make_context_current(window)
    glfw.swap_interval(1)  # // Enable vsync

    
    # Setup Dear ImGui context
    # IMGUI_CHECKVERSION();
    imgui.create_context()
    io = imgui.get_io()
    io.config_flags |= (
        imgui.ConfigFlags_.nav_enable_keyboard.value
    )  # Enable Keyboard Controls
    
        
    # io.config_flags |= imgui.ConfigFlags_.nav_enable_gamepad # Enable Gamepad Controls
    io.config_flags |= imgui.ConfigFlags_.docking_enable   # Enable docking
    io.config_flags |= imgui.ConfigFlags_.viewports_enable # Enable Multi-Viewport / Platform Windows
    # io.config_flags |= imgui.ConfigFlags_.dpi_enable_scale_fonts
    # io.config_flags |= imgui.ConfigFlags_.dpi_enable_scale_viewports
    
    # Setup Dear ImGui style
    imgui.style_colors_dark()
    # imgui.style_colors_classic()

    # When viewports are enabled we tweak WindowRounding/WindowBg so platform 
    # windows can look identical to regular ones.
    style = imgui.get_style()
    if io.config_flags & imgui.ConfigFlags_.viewports_enable.value:
        style.window_rounding = 4.0
        window_bg_color = style.color_(imgui.Col_.window_bg.value)
        window_bg_color.w = 1.0
        style.set_color_(imgui.Col_.window_bg.value, window_bg_color)

    # Setup Platform/Renderer backends
    import ctypes

    # You need to transfer the window address to imgui.backends.glfw_init_for_opengl
    # proceed as shown below to get it.
    window_address = ctypes.cast(window, ctypes.c_void_p).value
    assert window_address is not None
    imgui.backends.glfw_init_for_opengl(window_address, True)

    imgui.backends.opengl3_init(glsl_version)


    # Add Fonts
    load_icon_fonts()
    
    
    # Initialize ModernGL context
    ctx = moderngl.create_context()
    
    ctx.enable(flags=moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)  
    
    
    # Create a framebuffer to render the scene
    viewport_width, viewport_height = 800, 600 # Just Random Initial Values
    fbo, fbo_texture = create_framebuffer(ctx, viewport_width, viewport_height)
    
    oldview_size = (viewport_width, viewport_height)
        
        
    # Create Scene -------------------------------------------------------------

    # Create Camera
    viewport_camera = PyImOGuizmo.Camera( viewport_width/viewport_height, 
                                          position = (0, 1, 15), 
                                          pitch    = 0, 
                                          yaw      = -90)    
    
    viewport_camera.FOV = 45
    
    # Simple Scene Manager
    list_entities   = [] 
    selected_entity = None
    
    # Create a Grid Helper
    view_grid = Mesh.MeshGrid()
    list_entities.append(view_grid)
    
    # Create an Axes Helper
    view_reference_axes = Mesh.MeshAxes()
    list_entities.append(view_reference_axes)
    
    this_dir = os.path.dirname(__file__)
    textures = {}
    textures['texture_wood']  = create_texture(ctx, this_dir + '/assets/textures/img.png')
    textures['texture_metal'] = create_texture(ctx, this_dir + '/assets/textures/img_1.png')
    textures['texture_test']  = create_texture(ctx, this_dir + '/assets/textures/test.png')
    
    box_test = Mesh.MeshCube("Wood Box", textures['texture_wood'])
    box_test.position = (-5, 0, 0)
    list_entities.append(box_test)

    box_test = Mesh.MeshCube("Metal Box", textures['texture_metal'])
    box_test.position = ( 5, 0, 0)
    list_entities.append(box_test)
    
    box_test = Mesh.MeshCube("Test Box", textures['texture_test'])
    list_entities.append(box_test)
    
    
    # ==========================================================================
    # Main loop 
    # ==========================================================================
    while not glfw.window_should_close(window):

        glfw.poll_events()

        # Start the Dear ImGui frame
        imgui.backends.opengl3_new_frame()
        imgui.backends.glfw_new_frame()
        imgui.new_frame()
                
        
        # Enable Docking Space in the Main Viewport
        imgui.dock_space_over_viewport(dockspace_id=0, 
                                       viewport = imgui.get_main_viewport())
        
        # Enable to move windows only from the title bar
        imgui.get_io().config_windows_move_from_title_bar_only = True
        
        
        # # Process Inputs
        # process_key_press()
        
        
        # Init the main menu
        create_main_menu()
        
        
        # Show/Hide the ImGui Demo Window
        if app_state.show_imgui_demo: 
            app_state.show_imgui_demo = imgui.show_demo_window(app_state.show_imgui_demo)


        # # Update Views ------------------------------------------------------- 
        # for curview in list_views:
        #     curview.update()


        # Render Views -------------------------------------------------------     
        # for curview in list_views:
        #     curview.render()
        
        
        # 3D Viewport View
        if imgui.begin(f'{icons_fontawesome.ICON_FA_CUBES} 3D Viewport'):


            view_size = imgui.get_content_region_avail()
            
            
            # Recreate the framebuffer when the window's size has changed
            if view_size != oldview_size:
                
                # Sanity Check: Avoid that the any of the size of the framebuffer 
                # be less than 20
                view_size.x = 20 if view_size.x < 20 else view_size.x
                view_size.y = 20 if view_size.y < 20 else view_size.y
                
                # Free Memory
                fbo.release()
                fbo_texture.release()
                
                # Recreate the new frame buffer
                fbo, fbo_texture = create_framebuffer(ctx, 
                                                    int(view_size.x), 
                                                    int(view_size.y))
                
                # Update teh Camera Aspect Ratio
                viewport_camera.aspect_ratio = view_size.x / view_size.y
                
                # Store the size of the new frame buffer
                oldview_size = (int(view_size.x), int(view_size.y)) 
                
            
            # Bind the Frame Buffer to render the viewport into the texture
            fbo.use()
            ctx.viewport = (0, 0, view_size.x, view_size.y)
            ctx.clear(0.125, 0.125, 0.125, 1.0)  # Clear the framebuffer / Background Color of the 3D Viewport

                                        
            #  Render the Scene      
            for cur_object in list_entities:
                cur_object.render(viewport_camera)
                
            
            # Unbind the Framebuffer
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)


            # Display the FBO texture in ImGui Widget
            imgui.image(fbo_texture.glo,            # Texture ID
                        (view_size.x, view_size.y), (0,1), (1,0)) # Flip Texture to convert from 
                                                                  # OpenGL's Bottom-Left -> Top-Right
                                                                  # to ImGui's Top-Left -> Bottom-Right
                                                                           
            rect_min  = imgui.get_item_rect_min()
            rect_max  = imgui.get_item_rect_max()
            
    
            # Display Overlay Extra Info  
            display_overlay_extra_info(imgui.is_item_hovered(), 
                                       imgui.is_window_focused(),
                                       imgui.get_window_pos(), 
                                       viewport_camera.position)


            # Set Rotation Sensitivity 
            PyImOGuizmo.config.yaw_rotation_speed   = 0.25 #0.005
            PyImOGuizmo.config.pitch_rotation_speed = 0.25 #0.003
            
            
            # Pass the draw list of the current window to the PyImOGuizmo
            PyImOGuizmo.set_draw_list()

            # Set the location of the Gizmo
            PyImOGuizmo.set_rect( rect_max.x - 80 - 40, 
                                  rect_min.y, 
                                  80)

            # PyImOGuizmo.begin_frame()
            
            
            if not  app_state.use_imoguizmo_camera_version:
                
                PyImOGuizmo.config.yaw_rotation_speed   = 0.005
                PyImOGuizmo.config.pitch_rotation_speed = 0.003
                
                is_view_changed,  new_view_matrix, is_gizmo_hovered, is_gizmo_dragged = PyImOGuizmo.draw_gizmo(viewport_camera.get_view_matrix(), 10)
                
                if(is_view_changed):
                    
                    yaw, pitch, roll  = PyImOGuizmo.compute_euler_angles_from_view_matrix(new_view_matrix)
                    
                    viewport_camera.yaw   = glm.degrees(yaw) 
                    viewport_camera.pitch = glm.degrees(pitch)
                        
                    viewport_camera.update_camera_vectors()    
                
            else: 
                is_view_changed, is_gizmo_hovered, is_gizmo_dragged = PyImOGuizmo.draw_gizmo_camera(viewport_camera)
                
                # if(is_view_changed):    
                #     viewport_camera.update_camera_vectors()  
                
            imgui.end()



        # Scene Manager View 
        if imgui.begin(f'{icons_fontawesome.ICON_FA_CODE_BRANCH} Scene Manager'):
            
            #  Deselect any selection when mouse is clicked outside the Node Tree
            if imgui.is_mouse_down(imgui.MouseButton_.left) and imgui.is_window_hovered() and not imgui.is_any_item_hovered():
                selected_entity = None
                
            imgui.push_style_var(imgui.StyleVar_.indent_spacing, 6)
            
            if imgui.tree_node_ex("Scene", imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.allow_overlap | imgui.TreeNodeFlags_.frame_padding | imgui.TreeNodeFlags_.span_full_width): 
                
                
                for cur_entity in list_entities:
                
                    imgui.tree_push(cur_entity.id)
                    
                    _, cur_selected = imgui.selectable(f'\uf1b2  {cur_entity.name}', 
                                                            True if cur_entity == selected_entity else False, 
                                                            imgui.SelectableFlags_.allow_overlap | imgui.SelectableFlags_.span_all_columns)
                            
                    if(cur_selected):
                        selected_entity = cur_entity
                        
                    imgui.same_line()
                    imgui.dummy( ( imgui.get_content_region_avail().x - 40, 0) )
                    imgui.same_line()
                    _, cur_entity.visible = imgui.checkbox("##node_visible", cur_entity.visible)
                    
                    imgui.tree_pop()
                
                
                imgui.tree_pop()
            
            imgui.pop_style_var()
            
            imgui.end()

                # Property Inspector View 
        
        
        
        # PyImOGuizmo's Options View 
        if imgui.begin(f'{icons_fontawesome.ICON_FA_SYNC} PyImOGuizmos Options' ):
            
            # PyImOGuizmo's Property
            imgui.separator_text("Type")
            
            if (imgui.radio_button("Camera Version", app_state.use_imoguizmo_camera_version == True)):
                app_state.use_imoguizmo_camera_version = True
            imgui.same_line()
            if(imgui.radio_button("View Matrix Version", app_state.use_imoguizmo_camera_version == False)):
                app_state.use_imoguizmo_camera_version = False
            
            imgui.separator_text("Flags")
            imgui.text("Hovered: ")
            imgui.same_line()
            imgui.text_colored((1,1,0,1) if is_gizmo_hovered else (0.5,.5,.5,1), str(is_gizmo_hovered) )
            
            imgui.text("Dragged: ")
            imgui.same_line()
            imgui.text_colored((1,1,0,1) if is_gizmo_dragged else (0.5,.5,.5,1), str(is_gizmo_dragged) )
            
            imgui.text("ViewMatrix Changed: ")
            imgui.same_line()
            imgui.text_colored((1,1,0,1) if is_view_changed else (0.5,.5,.5,1), str(is_view_changed) )
            
            imgui.end()



        # Property Inspector View 
        if imgui.begin(f'{icons_fontawesome.ICON_FA_SLIDERS_H} Property Inspector' ):
                        
            # Camera's Property
            imgui.separator_text("Camera's Properties")
            
            _, viewport_camera.FOV = imgui.drag_float( LabelPrefix( "FOV" ), viewport_camera.FOV)
            
            pos_changed, new_pos= imgui.drag_float3( LabelPrefix( "Position"), viewport_camera.position, v_speed=0.01)
            if pos_changed:
                viewport_camera.position = glm.vec3(new_pos)
                
            changed, new_pitch  = imgui.drag_float( LabelPrefix( "Pitch"), viewport_camera.pitch,  v_speed=0.1, format="%.1f deg")
            if changed:
                viewport_camera.pitch = new_pitch
                viewport_camera.update_camera_vectors()
            
            changed, new_yaw  = imgui.drag_float( LabelPrefix( "Yaw"), viewport_camera.yaw,  v_speed=0.1, format="%.1f deg")
            if changed:
                viewport_camera.yaw = new_yaw
                viewport_camera.update_camera_vectors()
                
            imgui.spacing()
            
            # Selected Entity's Property
            if(selected_entity):
                imgui.separator_text(f"{selected_entity.name}'s Properties")
                
                if not isinstance(selected_entity, Mesh.MeshGrid):
                    _, selected_entity.position = imgui.drag_float3("Position##selectedentity", selected_entity.position, v_speed=0.01)
                
                _, selected_entity.visible = imgui.checkbox("Visible##selectedentity", selected_entity.visible)
                
            imgui.end()
        
        
        
        # ImGui Rendering ------------------------------------------------------
        imgui.render()

        
        imgui.backends.opengl3_render_draw_data(imgui.get_draw_data())


        # Update and Render additional Platform Windows
        # (Platform functions may change the current OpenGL context, so we save/restore
        # it to make it easier to paste this code elsewhere. For this specific 
        # demo app we could also call glfwMakeContextCurrent(window) directly)
        if io.config_flags & imgui.ConfigFlags_.viewports_enable.value > 0:
            backup_current_context = glfw.get_current_context()
            imgui.update_platform_windows()
            imgui.render_platform_windows_default()
            glfw.make_context_current(backup_current_context)
        
        glfw.swap_buffers(window)

    
    
    # Cleanup
    fbo_texture.release()
    fbo.release()
    
    for cur_texture in textures.values():
        cur_texture.release()
        
    for cur_entity in list_entities:
        cur_entity.release()
    
    imgui.backends.opengl3_shutdown()
    imgui.backends.glfw_shutdown()
    
    # 
    imgui.destroy_context()
    
    # 
    glfw.destroy_window(window)
    glfw.terminate()



if __name__ == "__main__":
    main()
