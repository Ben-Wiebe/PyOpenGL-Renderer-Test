from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import numpy as np
import time

class ChunkGenerator:

    def __init__(self, terrain_program):

        self.terrain_program = terrain_program
        self.sobel_strength = 1


    def generate(self, size, pos, step_size):
        st = time.time()

        #-----------HEIGHTMAP---------------------
        heightmap = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, heightmap)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 65, 65, 0, GL_RGBA, GL_FLOAT, None)
        glBindImageTexture(0, heightmap, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

        #-----------NORMALMAP---------------------
        normalmap = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, normalmap)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 65, 65, 0, GL_RGBA, GL_FLOAT, None)
        glBindImageTexture(1, normalmap, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

        #-----------COMPUTE-UNIFORMS---------------
        glUseProgram(self.terrain_program)

        chunk_x_loc = glGetUniformLocation(self.terrain_program, "chunk_x")
        chunk_y_loc = glGetUniformLocation(self.terrain_program, "chunk_y")
        chunk_s_loc = glGetUniformLocation(self.terrain_program, "chunk_size")
        chunk_step_loc = glGetUniformLocation(self.terrain_program, "step_size")
        norm_strength_loc = glGetUniformLocation(self.terrain_program, "sobel_strength")

        glUniform1f(chunk_x_loc, pos[0])
        glUniform1f(chunk_y_loc, pos[1])
        glUniform1f(chunk_s_loc, size)
        glUniform1f(chunk_step_loc, step_size)
        glUniform1f(norm_strength_loc, self.sobel_strength)

        #-----------DISPATCH-COMPUTE---------------
        glDispatchCompute(65, 65, 1)
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        
        print(f"compute in {time.time()-st}s")

        return heightmap, normalmap
        

if __name__ == "__main__":
    g = ChunkGenerator()
    g.generate( 16, (0, 0), 1 )
