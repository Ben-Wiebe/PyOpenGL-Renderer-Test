from pyrr import Matrix44, Quaternion, Vector3, vector
import numpy as np

class Camera:
    def __init__(self, ratio):
        self.move_vertically = 1
        self.move_horizontally = 3#0.08
        self._rotate_horizontally = 0.18
        self._rotate_vertically = 0.18

        self.view_wireframe = False

        self.move_enabled = True
        self.last_x = 0
        self.last_y = 0

        #                north, south, east,  west,  up,    down
        self.movement = [False, False, False, False, False, False]

        self.grounded = True
        self.jumping = False
        self.vy = 0

        self._field_of_view_degrees = 75.0
        self._z_near = 0.1
        self._z_far = 15000
        self._ratio = ratio
        self.build_projection()

        self.camera_position = Vector3([0.0, 10.0, 0.0])
        self._camera_front = Vector3([0.0, 0.0, 1.0]) # Projection Plane
        self._camera_up = Vector3([0.0, 1.0, 0.0])
        self._move_vector = Vector3([1.0, 0.0, 1.0]) # Allows movement forwards/backwards to affect only x/z axis, not y
        self._cameras_target = (self.camera_position + self._camera_front)
        self.build_look_at()
        
    def move_forwards(self):
        self.camera_position = self.camera_position + self._camera_front * self.move_horizontally * self._move_vector
        self.build_look_at()

    def move_backwards(self):
        self.camera_position = self.camera_position - self._camera_front * self.move_horizontally * self._move_vector
        self.build_look_at()

    def strafe_left(self):
        self.camera_position = self.camera_position - vector.normalize(self._camera_front ^ self._camera_up) * self.move_horizontally
        self.build_look_at()

    def strafe_right(self):
        self.camera_position = self.camera_position + vector.normalize(self._camera_front ^ self._camera_up) * self.move_horizontally
        self.build_look_at()

    def strafe_up(self):
        self.camera_position = self.camera_position + self._camera_up * self.move_vertically
        self.build_look_at()

    def strafe_down(self):
        self.camera_position = self.camera_position - self._camera_up * self.move_vertically
        self.build_look_at()

    def rotate_left(self, d):
        rotation = Quaternion.from_y_rotation(d * float(self._rotate_horizontally) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def rotate_right(self, d):
        rotation = Quaternion.from_y_rotation(-d * float(self._rotate_horizontally) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def rotate_horizontal(self, d):
        rotation = Quaternion.from_y_rotation(-d * float(self._rotate_horizontally) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def rotate_up(self):
        rotation = Quaternion.from_x_rotation(-2 * float(self._rotate_vertically) * np.pi / 180)
        self._camera_front = rotation * self._camera_front# * self._camera_up
        self.build_look_at()

    def rotate_down(self):
        rotation = Quaternion.from_x_rotation(2 * float(self._rotate_vertically) * np.pi / 180)
        self._camera_front = rotation * self._camera_front# * self._camera_up
        self.build_look_at()

    def rotate_vertical(self, d):
        rotation = Quaternion.from_x_rotation(d * float(self._rotate_vertically) * np.pi / 180)
        #self._camera_front[1] = min(1, max(-1, (rotation * self._camera_front)[1]))
        self._camera_front[1] = min(2.5, max(-2.5, self._camera_front[1] + 0.005*-d))
        self.build_look_at()

    def move_up(self):
        self.camera_position += Vector3([0, self.move_vertically, 0])
        self.build_look_at()

    def move_down(self):
        self.camera_position -= Vector3([0, self.move_vertically, 0])
        self.build_look_at()

    def build_look_at(self):
        self._cameras_target = (self.camera_position + self._camera_front)
        self.mat_lookat = Matrix44.look_at(
            self.camera_position,
            self._cameras_target,
            self._camera_up)

    def build_projection(self):
        self.mat_projection = Matrix44.perspective_projection(
            self._field_of_view_degrees,
            self._ratio,
            self._z_near,
            self._z_far)
