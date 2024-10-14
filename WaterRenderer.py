from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from FileLoader import *

class WaterRenderer:

    loader = Loader()

    RELFECTION_FBO_SIZE = [320, 180]
    REFRACTION_FBO_SIZE = [1280, 720]
    
    def __init__(self):
        self.debug = False

        self.reflection_fb = None
        self.refraction_fb = None
        self.reflection_texture = None
        self.reflection_depth_texture = None

        self.init_reflection_frame_buffer()
        self.init_refraction_frame_buffer()

    def init_reflection_frame_buffer(self):
        # create reflection buffer
        self.reflection_fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.reflection_fb)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)

        # create reflection texture attachment
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     self.REFLECTION_FBO_SIZE[0], self.REFLECTION_FBO_SIZE[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, texture)

        self.reflection_texture = texture

        # create reflection depth texture attachment
        reflection_depth_buffer = glGenRenderbuffers()
        glBindRenderbuffer(GL_RENDERBUFFER, reflection_depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT,
                              self.REFLECTION_FBO_SIZE[0], self.REFLECTION_FBO_SIZE[1])
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER,
                                  reflection_depth_buffer)

        self.reflection_depth = reflection_depth_buffer

        # unbind reflection frame buffer
        self.unbind()

    def init_refraction_frame_buffer(self):
        # create refraction buffer
        self.refraction_fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.refraction_fb)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)

        # create refraction texture attachment
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     self.REFRACTION_FBO_SIZE[0], self.REFRACTION_FBO_SIZE[1],
                     0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, texture)

        self.refraction_texture = texture

        # create refraction depth texture attachment
        refraction_depth_texture = glGenTextures()
        glBindTexture(GL_TEXTURE_2D, refraction_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32,
                     self.REFRACTION_FBO_SIZE[0], self.REFRACTION_FBO_SIZE[1],
                     0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT0, refraction_depth_texture, 0)

        self.refraction_depth = refraction_depth_texture

        # unbind refraction frame buffer
        self.unbind()

    def bind_reflection(self):
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, self.reflection_fb)
        glViewport(0, 0, self.REFLECTION_FBO_SIZE[0], self.REFLECTION_FBO_SIZE[1])

    def bind_refraction(self):
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, self.refraction_fb)
        glViewport(0, 0, self.REFRACTION_FBO_SIZE[0], self.REFRACTION_FBO_SIZE[1])

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, 1920, 1080)
        
