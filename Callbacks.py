import glfw

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

# the mouse position callback function
def mouse_look_clb(window, xpos, ypos):

    xoffset = xpos - camera.last_x
    yoffset = ypos - camera.last_y

    camera.last_x = xpos
    camera.last_y = ypos

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
    
