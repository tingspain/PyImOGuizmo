"""
File Name: mesh.py
Author: JuanMa Romero Martin <juanma@ihm.solutions>
Date Created:  2025-02-15
Last Modified: 2025-03-01
Description: This module contains the implementation of various Mesh classes, 
             including base Mesh, MeshCube, MeshGrid, and MeshAxes, used for 
             rendering 3D objects.

TODO: 
    - 
"""

import moderngl 
import glm
import uuid

import geometry as Geometry
from PyImOGuizmo import Camera
from shader_program import ShaderProgram



class Mesh():
    
    VERTEX_SHADER_SRC = """
    #version 330 core

    layout (location = 0) in vec2 in_texcoord_0;
    layout (location = 1) in vec3 in_normal;
    layout (location = 2) in vec3 in_position;

    out vec3 ourColor;
    out vec2 TexCoord;

    uniform vec3 in_color = vec3(1, 0, 0);
    uniform mat4 in_m_proj;
    uniform mat4 in_m_view;
    uniform mat4 in_m_model;

    void main() {
        gl_Position = in_m_proj * in_m_view * in_m_model * vec4(in_position, 1.0);
        ourColor = in_color * in_normal;
        TexCoord = in_texcoord_0;
    }
    """

    FRAGMENT_SHADER_SRC = """
    #version 330 core

    out vec4 finalColor;

    in vec2 TexCoord;
    in vec3 ourColor;

    uniform bool in_use_texture = false;
    uniform sampler2D u_texture_0;

    void main() {
        float gamma = 2.2;
        vec3 color = ourColor;
        if(in_use_texture == true){
            color = texture(u_texture_0, TexCoord).rgb;
        }  
            
        color = pow(color, vec3(gamma));
        color = pow(color, 1 / vec3(gamma));
        finalColor =  vec4(color, 1.0);
    }
    """
    
    def __init__(self, program, geometry: Geometry, texture=None):
        """_summary_

        Args:
            program (_type_): _description_
            geometry (Geometry): _description_
            texture (_type_, optional): _description_. Defaults to None.
        """
        
        self.id:str       = str( uuid.uuid4() )
        self.name:str     = "Base Mesh"
        self.visible:bool = True
        
        self.ctx     = moderngl.get_context()
        self.vao     = geometry.vertex_array(program)
        self.texture = texture
        
        self.color       = (1.0, 0.5, 0.5)
        self.position    = (0, 0, 0)
        self.scale       = (1, 1, 1)
        self.rotation    = glm.vec3(0, 0, 0)
        self.translation = (0, 0, 0)   
        
        self.render_mode = moderngl.TRIANGLES     
        
        
    def get_model_matrix(self):
        
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.position)
        
        # scale
        m_model = glm.scale(m_model, self.scale)
        
        # rotate
        m_model = glm.rotate(m_model, self.rotation.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rotation.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rotation.x, glm.vec3(1, 0, 0))


     
        return m_model
    
    
    def render(self, camera:Camera):
        
        if not self.visible:
            return
        
        # self.vao.program[ShaderProgram.ATTRIBS_.USE_TEXTURE] = False

        if self.texture:
            self.vao.program[ShaderProgram.ATTRIBS_.USE_TEXTURE] = True
            self.texture.use()
        
        self.vao.program[ShaderProgram.ATTRIBS_.M_PROJECTION].write( camera.get_projection_matrix() )
        self.vao.program[ShaderProgram.ATTRIBS_.M_VIEW].write( camera.get_view_matrix() )
        self.vao.program[ShaderProgram.ATTRIBS_.M_MODEL].write( self.get_model_matrix() ) 
        self.vao.program[ShaderProgram.ATTRIBS_.POSITION] = self.position
        self.vao.program[ShaderProgram.ATTRIBS_.COLOR]    = glm.vec3(0.5, 0.5, 0.5)
        
        self.vao.render(self.render_mode)
        
        
    def release(self):
        self.vao.release()

        
        
class MeshCube(Mesh):
    
     def __init__(self, name="Mesh Cube", texture=None):
        
        super().__init__(moderngl.get_context().program(
                            vertex_shader   = Mesh.VERTEX_SHADER_SRC,
                            fragment_shader = Mesh.FRAGMENT_SHADER_SRC
                        ), 
                        Geometry.CubeGeometry(moderngl.get_context()), 
                        texture
                        ) 
        
        self.name = name
        
         
        
class MeshGrid(Mesh):
    
    VERTEX_SHADER_SRC = """
    #version 330 core

    layout (location = 0) in vec3 in_position;

    out vec3 ourColor;

    uniform vec3 in_color = vec3(1, 0, 0);
    uniform mat4 in_m_proj;
    uniform mat4 in_m_view;
    uniform mat4 in_m_model;

    void main() {
        gl_Position = in_m_proj * in_m_view * in_m_model * vec4(in_position, 1.0);
        ourColor = in_color;
    }
    """

    FRAGMENT_SHADER_SRC = """
    #version 330 core

    out vec4 finalColor;

    in vec3 ourColor;


    void main() {
        float gamma = 2.2;
        vec3 color = ourColor;        
        color = pow(color, vec3(gamma));
        color = pow(color, 1 / vec3(gamma));
        finalColor =  vec4(color, 1.0);
    }
    """
    
    
    def __init__(self, name = "Mesh Grid", asize=50, asteps=100):
        super().__init__(moderngl.get_context().program(
                            vertex_shader   = MeshGrid.VERTEX_SHADER_SRC,
                            fragment_shader = MeshGrid.FRAGMENT_SHADER_SRC
                        ), 
                        Geometry.GridGeometry(moderngl.get_context(), size=asize, steps=asteps), 
                        ) 
        
        self.name = "Grid Helper"
        
        
    def render(self, camera:Camera):

        if not self.visible:
            return
        
        self.vao.program[ShaderProgram.ATTRIBS_.M_PROJECTION].write(camera.get_projection_matrix())
        self.vao.program[ShaderProgram.ATTRIBS_.M_VIEW].write(camera.get_view_matrix())
        self.vao.program[ShaderProgram.ATTRIBS_.POSITION] = self.position
        self.vao.program[ShaderProgram.ATTRIBS_.COLOR]    = glm.vec3(0.5, 0.5, 0.5)
        # self.vao.program[ShaderProgram.ATTRIBS_.M_MODEL].write( glm.rotate( glm.radians(-90), (1,0,0)) ) 
        
        self.vao.program[ShaderProgram.ATTRIBS_.M_MODEL].write( glm.mat4() ) #  glm.rotate() * glm.scale() * glm.translate()
        
        self.vao.render(moderngl.LINES)
        


class MeshAxes(Mesh):
    
    VERTEX_SHADER_SRC = """
    #version 330 core

    layout (location = 0) in vec3 in_color;
    layout (location = 1) in vec3 in_position;

    out vec3 ourColor;

    uniform mat4 in_m_proj;
    uniform mat4 in_m_view;
    uniform mat4 in_m_model;

    void main() {
        gl_Position = in_m_proj * in_m_view * in_m_model * vec4(in_position, 1.0);
        ourColor = in_color;
    }
    """

    FRAGMENT_SHADER_SRC = """
    #version 330 core

    out vec4 finalColor;

    in vec3 ourColor;


    void main() {
        float gamma = 2.2;
        vec3 color = ourColor;        
        color = pow(color, vec3(gamma));
        color = pow(color, 1 / vec3(gamma));
        finalColor =  vec4(color, 1.0);
    }
    """
    
    def __init__(self):
        super().__init__(moderngl.get_context().program(
                    vertex_shader   = self.VERTEX_SHADER_SRC,
                    fragment_shader = self.FRAGMENT_SHADER_SRC
                ), 
                Geometry.AxisGeometry(moderngl.get_context()), 
                ) 
        
        self.name = "Axes Helper"
        self.render_mode = moderngl.LINES
        
       
        