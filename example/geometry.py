"""
File Name: Geometry.py
Author: Me <some@user.com>
Date Created:  2025-02-15
Last Modified: 2025-02-15
Description: This module provides an abstract base class `Geometry` for handling geometric shapes 
             in a rendering context. It includes functionality to initialize vertex buffer objects (VBOs),
             manage vertex attributes, and create vertex arrays. Subclasses are required to implement 
             methods to specify attribute formats, attribute lists, and vertex array creation.
"""

import numpy as np
import moderngl as mgl
from abc import ABC


#-------------------------------------------------------------------------------
#    S I M P L E      V E R T E C I S      B A S E D      G E O M E T R Y 
#-------------------------------------------------------------------------------


class Geometry(ABC):
    """
    Geometry class

    This abstract base class provides common functionality for handling geometric shapes in a rendering context.
    It initializes vertex buffer objects (VBOs), manages vertex attributes, and creates vertex arrays.

    Attributes:
        ctx: The rendering context in which the geometry is created.
        __vertices (np.array): The array of vertices for the geometry.
        __vbo: The Vertex Buffer Object created from the vertices.
        __attributes (list): The list of attribute names for the vertex data.
        __attributes_format (str): The format of the vertex attributes.
    """

    def __init__(self, ctx:mgl.Context):
        """
        Initializes the Geometry with the given context and creates a VBO.

        Args:
            ctx: The rendering context in which the geometry is created.
        """
        
        super().__init__()
    
        self.ctx      = ctx
        self.vertices = np.array([
                                -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                                0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
                                -0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
                                -0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
                                0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
                                0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
                            ])
        self.vbo = self.ctx.buffer(self.vertices.astype('f4').tobytes())
        
        # TODO: Change to attr_names
        self.attributes        = ['in_position', 'in_texcoord_0']
        
        # TODO: Change to attr_format
        self.attributes_format = '3f 12x 2f'


    def get_attributes_format(self):
        """
        This method should be overridden by subclasses to provide the format of the vertex attributes.

        Returns:
            The format of the vertex attributes.
        """
        return self.attributes_format
        
        
    def get_attributes(self):
        """
        This method should be overridden by subclasses to provide the list of attribute names for the vertex data.

        Returns:
            The list of attribute names for the vertex data.
        """
        return self.attributes    
        
        
    def vertex_array(self, program) -> mgl.VertexArray:
        """
        Creates a vertex array from the given shader program and VBO.

        Args:
            program: The shader program to be used for the vertex array.

        Returns:
            The created Vertex Array Object.
        """
        return self.ctx.vertex_array(program, [ 
                                                 ( self.vbo, 
                                                   self.attributes_format, 
                                                   *self.attributes ) 
                                                 ])
    
    
    def get_data(self, vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')


    def destroy(self):
        """
        Releases the VBO.
        """
        self.vbo.release()
        
               
class CubeGeometry(Geometry):
    
    def __init__(self, ctx):
        
        super().__init__(ctx)
        
        vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]

        indices = [(0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6)]
        vertex_data = self.get_data(vertices, indices)

        tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                                (0, 2, 3), (0, 1, 2),
                                (0, 1, 2), (2, 3, 0),
                                (2, 3, 0), (2, 0, 1),
                                (0, 2, 3), (0, 1, 2),
                                (3, 1, 2), (3, 0, 1),]
        tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)

        normals = [( 0, 0, 1) * 6,
                    ( 1, 0, 0) * 6,
                    ( 0, 0,-1) * 6,
                    (-1, 0, 0) * 6,
                    ( 0, 1, 0) * 6,
                    ( 0,-1, 0) * 6,]
        
        self.normals  = np.array(normals, dtype='f4').reshape(36, 3)
        vertex_data   = np.hstack([self.normals, vertex_data])
        vertex_data   = np.hstack([tex_coord_data, vertex_data])
        self.vertices = vertex_data
        
        self.vbo = ctx.buffer(self.vertices.tobytes()) 
        
        self.attributes        = ['in_texcoord_0', 'in_normal', 'in_position']
        self.attributes_format = '2f 3f 3f'

  
class GridGeometry(Geometry):
    
    def __init__(self, ctx:mgl.Context, size=50, steps=50):
        
        self.ctx      = ctx
        self.size     = size
        self.steps    = steps
        self.vertices = self.grid( size, steps).astype('f4')
        
        self.vbo = self.ctx.buffer(self.vertices)
    
        self.attributes = ['in_position']
        self.attributes_format = '3f'
        
        
    def grid(self, size, steps):
        u = np.repeat(np.linspace(-size, size, steps), 2)
        v = np.tile([-size, size], steps)
        w = np.zeros(steps * 2)
        # return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])
        return np.concatenate([np.dstack([u, w, v]), np.dstack([v, w, u])])
    
    
class AxisGeometry(Geometry):
     
    def __init__(self, ctx:mgl.Context, size:int = 4, up=( 0, 1, 0)):
        
        self.ctx      = ctx
        self.color_axis_x = np.array((1, 0, 0))
        self.color_axis_y = np.array((0, 1, 0))
        self.color_axis_z = np.array((0, 0, 1))
        
        self.vertices = self.generate_axis(size, up).astype('f4')
        
        self.vbo = self.ctx.buffer(self.vertices)
    
        
        self.attributes = ['in_color', 'in_position']
        self.attributes_format = '3f 3f'
        
        
    def generate_axis(self, size:int = 1, up=( 0, 1, 0)):
        vertices = []
        vertices.append( np.array( [ self.color_axis_x, [size,    0.005,    0], self.color_axis_x, [ 0, 0.005, 0] ] ) )
        vertices.append( np.array( [ self.color_axis_y, [   0, size,    0], self.color_axis_y, [ 0, 0.005, 0] ] ) )
        vertices.append( np.array( [ self.color_axis_z, [   0,    0.005, size], self.color_axis_z, [ 0, 0.005, 0] ] ) )
        return np.concatenate(vertices)
     
     