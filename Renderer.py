from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

import time

import PIL

from FileLoader import *
from WaterRenderer import *
from Quadtree import *

class Renderer:
    
    loader = Loader()
    #water_render = WaterRenderer()
    
    def __init__(self, camera, chunk_gen):
        self.debug = False

        self.camera = camera
        self.quadtree = Quadtree(camera, chunk_gen, base_size=8192*4)
        
        self.skybox_vao, self.skybox_vbo = self.init_skybox()
        self.init_terrain()
        
        self.factor = 0.7

    def skybox_bind(self, vao, vbo):
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    def terrain_bind(self, vao, vbo, ebo):
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        #glEnableVertexAttribArray(1)
        #glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        #glEnableVertexAttribArray(2)
        #glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

##        glEnableVertexAttribArray(3)
##        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(32))

    def init_skybox(self):
        self.loader.read_shader("skybox", "skybox_v_shader", "skybox_f_shader")
        faces = ["skybox3_px", "skybox3_nx", "skybox3_py", "skybox3_ny", "skybox3_pz", "skybox3_nz"]
        empty_face = ["box_empty", "box_empty", "box_empty", "box_empty", "box_empty", "box_empty"]
        alt_skybox = ["pos_x", "neg_x", "pos_y", "neg_y", "pos_z", "neg_z"]
        self.loader.read_cubemap("skybox", alt_skybox, ext=".png")
  
        size = 250
        skybox_verts = [
            -size,  size, -size,
            -size, -size, -size,
             size, -size, -size,
             size, -size, -size,
             size,  size, -size,
            -size,  size, -size,

            -size, -size,  size,
            -size, -size, -size,
            -size,  size, -size,
            -size,  size, -size,
            -size,  size,  size,
            -size, -size,  size,

             size, -size, -size,
             size, -size,  size,
             size,  size,  size,
             size,  size,  size,
             size,  size, -size,
             size, -size, -size,

            -size, -size,  size,
            -size,  size,  size,
             size,  size,  size,
             size,  size,  size,
             size, -size,  size,
            -size, -size,  size,

            -size,  size, -size,
             size,  size, -size,
             size,  size,  size,
             size,  size,  size,
            -size,  size,  size,
            -size,  size, -size,

            -size, -size, -size,
            -size, -size,  size,
             size, -size, -size,
             size, -size, -size,
            -size, -size,  size,
             size, -size,  size
        ]

        skybox_verts = np.array(skybox_verts, dtype=np.float32)
        skybox_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, skybox_vbo)
        glBufferData(GL_ARRAY_BUFFER, skybox_verts.nbytes, skybox_verts, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        skybox_vao = glGenVertexArrays(1)
        glBindVertexArray(skybox_vao)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, skybox_vbo)                                                                                          
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        return skybox_vao, skybox_vbo

    def render_skybox(self):
        glDepthFunc(GL_LEQUAL)
        glUseProgram(self.loader.shaders["skybox"])
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.loader.texture_ids["skybox"])
        self.skybox_bind(self.skybox_vao, self.skybox_vbo)

        proj_loc = glGetUniformLocation(self.loader.shaders["skybox"], "projection")
        view_loc = glGetUniformLocation(self.loader.shaders["skybox"], "view")
        fog_loc = glGetUniformLocation(self.loader.shaders["skybox"], "fog_colour")        

        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, self.camera.mat_projection)
        glUniform3fv(fog_loc, 1, pyrr.Vector3([214/255, 250/255, 255/255]))

        view_transform_mat = self.camera.mat_lookat
        view_transform_mat = pyrr.Matrix33.from_matrix44(view_transform_mat)
        view_transform_mat = pyrr.Matrix44.from_matrix33(view_transform_mat)
        
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_transform_mat)

        glVertexPointer(3, GL_FLOAT, 0, None)
        if not self.camera.view_wireframe:
            glDrawArrays(GL_TRIANGLES,  0, 36)
        elif self.camera.view_wireframe:
            glDrawArrays(GL_LINES,      0, 36)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDepthFunc(GL_LESS)

    def init_terrain(self):
        self.loader.read_shader("terrain", "terrain_v_shader2", "terrain_f_shader")
        self.loader.load_texture("terrain", self.loader.read_texture("grass_res", ".jpg"))
        self.loader.load_texture("terrain", self.loader.read_texture("stone_res", ".jpg"))
        self.loader.load_texture("terrain", self.loader.read_texture("snow_res", ".jpg"))
                
    def render_terrain(self):
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        current_shader = self.loader.shaders["terrain"]
        glUseProgram(current_shader)

        tex1_loc = glGetUniformLocation(current_shader, "grass_texture")
        tex2_loc = glGetUniformLocation(current_shader, "stone_texture")
        tex3_loc = glGetUniformLocation(current_shader, "snow_texture")
        tex4_loc = glGetUniformLocation(current_shader, "heightmap")
        tex5_loc = glGetUniformLocation(current_shader, "normalmap")
        
        glUniform1i(tex1_loc, 0)
        glUniform1i(tex2_loc, 1)
        glUniform1i(tex3_loc, 2)
        glUniform1i(tex4_loc, 3)
        glUniform1i(tex5_loc, 4)
        
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, self.loader.texture_ids["terrain"][0])
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, self.loader.texture_ids["terrain"][1])
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, self.loader.texture_ids["terrain"][2])

        model_loc = glGetUniformLocation(current_shader, "model")
        proj_loc = glGetUniformLocation(current_shader, "projection")
        view_loc = glGetUniformLocation(current_shader, "view")
        light_loc = glGetUniformLocation(current_shader, "Light")

        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, self.camera.mat_projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.camera.mat_lookat)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0])))
        glUniform3fv(light_loc, 1, self.camera.camera_position + pyrr.Vector3([0,10,0]))

        factor_loc = glGetUniformLocation(current_shader, "snow_factor")

        glUniform1f(factor_loc, self.factor)
        for i, chunk in self.quadtree.chunks.items():

            # Frustum Culling
            if not chunk.children:

                if True:

                    self.terrain_bind(chunk.vao, chunk.vbo, chunk.ebo)

                    glActiveTexture(GL_TEXTURE0 + 3)
                    glBindTexture(GL_TEXTURE_2D, chunk.heightmap)

                    glActiveTexture(GL_TEXTURE0 + 4)
                    glBindTexture(GL_TEXTURE_2D, chunk.normalmap)

                    if not self.camera.view_wireframe:
                        #glDrawArrays(GL_TRIANGLES, 0, 24576)
                        glDrawElements(GL_TRIANGLES, len(chunk.indices), GL_UNSIGNED_INT, None)
                    else:
                        glDrawElements(GL_LINES, len(chunk.indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

    def render_to_water(self):
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        #glUseProgram(self.loader.shaders["water"])

        #self.water_render.bind_reflection()
        self.render_terrain()
        self.render_skybox()
        #self.water_render.unbind()
