import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import time

from FileLoader import *
from camera import *
camera = Camera(16/9)
from Renderer import *
from ChunkGenerator import *

screen_res = (1920, 1080)
window_res = (1280,  720)

# the keyboard input callback
def key_input_clb(window, key, scancode, action, mode):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_W and action == glfw.PRESS:
        camera.movement[0] = True
    elif key == glfw.KEY_W and action == glfw.RELEASE:
        camera.movement[0] = False

    if key == glfw.KEY_S and action == glfw.PRESS:
        camera.movement[1] = True
    elif key == glfw.KEY_S and action == glfw.RELEASE:
        camera.movement[1] = False

    if key == glfw.KEY_A and action == glfw.PRESS:
        camera.movement[2] = True
    if key == glfw.KEY_A and action == glfw.RELEASE:
        camera.movement[2] = False

    if key == glfw.KEY_D and action == glfw.PRESS:
        camera.movement[3] = True
    if key == glfw.KEY_D and action == glfw.RELEASE:
        camera.movement[3] = False

    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        camera.movement[4] = True
    elif key == glfw.KEY_SPACE and action == glfw.RELEASE:
        camera.movement[4] = False

    if key == glfw.KEY_LEFT_SHIFT and action == glfw.PRESS:
        camera.movement[5] = True
    elif key == glfw.KEY_LEFT_SHIFT and action == glfw.RELEASE:
        camera.movement[5] = False

    if key == glfw.KEY_LEFT_CONTROL and action == glfw.PRESS:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        camera.move_enabled = False
    elif key == glfw.KEY_LEFT_CONTROL and action == glfw.RELEASE:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        camera.move_enabled = True

    if key == glfw.KEY_R and action == glfw.PRESS:
        camera.view_wireframe = True
    elif key == glfw.KEY_R and action == glfw.RELEASE:
        camera.view_wireframe = False

    if key == glfw.KEY_G and action == glfw.PRESS:
        renderer.factor += 0.01
    elif key == glfw.KEY_H and action == glfw.PRESS:
        renderer.factor -= 0.01

    if key == glfw.KEY_O and action == glfw.PRESS:
        glEnable(GL_FRAMEBUFFER_SRGB)
    elif key == glfw.KEY_P and action == glfw.PRESS:
        glDisable(GL_FRAMEBUFFER_SRGB)

    if key == glfw.KEY_L and action == glfw.PRESS:
        renderer.quadtree.compute_chunks([camera.camera_position[0], camera.camera_position[2]])

    if key == glfw.KEY_C and action == glfw.PRESS:
        camera.camera_position =  pyrr.Vector3([0,10,0])

# the mouse position callback function
def mouse_look_clb(window, xpos, ypos):

    xoffset = xpos - camera.last_x
    yoffset = ypos - camera.last_y

    camera.last_x = xpos
    camera.last_y = ypos

    if camera.move_enabled:

        camera.rotate_horizontal(xoffset)
        camera.rotate_vertical(yoffset)

def move_cam():
    if camera.movement[0]: camera.move_forwards()
    if camera.movement[1]: camera.move_backwards()
    if camera.movement[2]: camera.strafe_left()
    if camera.movement[3]: camera.strafe_right()
    if camera.movement[4]: camera.move_up()
    if camera.movement[5]: camera.move_down()

# glfw callback functions
def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(window_res[0], window_res[1], "My OpenGL window", None, None)
glfw.window_hint(glfw.SAMPLES, 4)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, (screen_res[0]//2) - (window_res[0]//2), (screen_res[1]//2) - (window_res[1]//2))

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

glfw.set_cursor_pos_callback(window, mouse_look_clb)
glfw.set_key_callback(window, key_input_clb)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# make the context current
glfw.make_context_current(window)

def gl_enables():
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_MULTISAMPLE)

    glEnable(GL_FRAMEBUFFER_SRGB)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def init_compute_gen():
    compute_gen = glCreateShader(GL_COMPUTE_SHADER)
    with open(f"shaders/compute_test.glsl") as file:
        compute_src = file.readlines()
    glShaderSource(compute_gen, compute_src, None)
    glCompileShader(compute_gen)
    if glGetShaderiv(compute_gen, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(compute_gen))

    terrain_program = glCreateProgram()
    glAttachShader(terrain_program, compute_gen)
    glLinkProgram(terrain_program) 
    print(glGetProgramInfoLog(terrain_program))

    return terrain_program

terrain_program = init_compute_gen()
chunk_gen = ChunkGenerator(terrain_program)
renderer = Renderer(camera, chunk_gen)

def main():
    
    gl_enables()
    
    previous_time = time.time()
    num_frames = 0

    while not glfw.window_should_close(window):
        glfw.poll_events()
        move_cam()

        #----------------------Render---------------------------
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        #renderer.quadtree.compute_chunks((camera.camera_position[0], camera.camera_position[2]))
        
        renderer.render_terrain()
        renderer.render_skybox()
        
        #--------------------Count  FPS-------------------------
        num_frames += 1
        current_time = time.time()
        delta_t = current_time - previous_time
        if delta_t > 1:
            glfw.set_window_title(window, f"3D Engine | FPS - {round(num_frames/delta_t)}")
            previous_time = current_time
            num_frames = 0
        
        #print(f"{delta_t} {1/120}s")
        if delta_t < 1/120:
            time.sleep((1/120)-delta_t)
        
        glfw.swap_buffers(window)
        
    glfw.terminate()

if __name__ == "__main__": main()
