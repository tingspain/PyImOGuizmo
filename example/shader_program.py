import os
from enum import StrEnum



class ShaderProgram:
    
    class ATTRIBS_(StrEnum):
        POSITION        = "in_position", 
        COLOR           = "in_color",
        UV              = "in_texcoord",
        M_MODEL         = "in_m_model",
        M_VIEW          = "in_m_view",
        M_PROJECTION    = "in_m_proj",
        USE_TEXTURE     = "in_use_texture",
        TEXTURE0        = "in_texture_0",
        LIGHT0_POSITION = "in_light0_position",
        LIGHT0_COLOR    = "in_light0_color",
        NEAR            = "in_near",
        FAR             = "in_far",
        GRID_BASE_SCALE = "in_grid_base_scale",
        MIN_GRID_SCALE  = "in_min_grid_scale",
        MAX_GRID_SCALE  = "in_max_grid_scale",
        

    
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = {}
        self.programs['default'] = self.get_program('default')

    def get_program(self, shader_program_name):
        
        this_dir = os.path.dirname(__file__)
        
        with open( this_dir +  f'/assets/shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open( this_dir + f'/assets/shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def destroy(self):
        [program.release() for program in self.programs.values()]
