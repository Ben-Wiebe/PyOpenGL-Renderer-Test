from OpenGL.GL import *
from OpenGL.GL.shaders import *#compileProgram, compileShader
import numpy as np
from PIL import Image

class Texture:
    def __init__(self, buffer, w, h):
        self.buffer = buffer
        self.w = w
        self.h = h

class Loader:
    def __init__(self):
        self.texture_ids = {}
        self.shaders = {}

    def read_shader(self, name, v_path, f_path, ext=".glsl"):
        with open(f"shaders/{v_path}{ext}") as file:
            vertex_src = file.readlines()

        with open(f"shaders/{f_path}{ext}") as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
 
        self.shaders[name] = shader

    def read_compute(self, name, path):
        with open(f"shaders/{path}.glsl") as file:
            compute_src = file.readlines()

        shader = compileShader(compute_src, GL_COMPUTE_SHADER)

        self.shaders[name] = shader

    def read_texture(self, path, ext=".jpg"):
        image = Image.open(f"textures/{path}{ext}")
        image_buffer = image.convert("RGBA").tobytes()
        return Texture(image_buffer, image.width, image.height)

    def load_texture(self, name, tex_object):

        tex_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     tex_object.w, tex_object.h, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     tex_object.buffer)
        glGenerateMipmap(GL_TEXTURE_2D)

        if not self.texture_ids.get(name):
            self.texture_ids[name] = []
        self.texture_ids[name].append(tex_id)

    def read_cubemap(self, name, face_paths, ext=".jpg", flip=False):
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)

        image_buffers = []
        for path in face_paths:
            image = Image.open(f"textures/{path}{ext}")
            width, height = image.width, image.height
            if flip: image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_buffers.append(image.convert("RGBA").tobytes())

        for i in range(6):
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGBA,
                         width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_buffers[i])

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        self.texture_ids[name] = tex_id
