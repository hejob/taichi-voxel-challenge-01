import time
import os
from datetime import datetime
import numpy as np
import taichi as ti
from renderer import Renderer
from math_utils import np_normalize, np_rotate_matrix
import math
import __main__

VOXEL_DX = 1 / 64
SCREEN_RES = (1280, 720)
TARGET_FPS = 30
UP_DIR = (0, 1, 0)
HELP_MSG = '''
====================================================
Camera:
* Drag with your left mouse button to rotate
* Press W/A/S/D/Q/E to move
====================================================
'''

MAT_LAMBERTIAN = 1
MAT_LIGHT = 2

class Camera:
    def __init__(self, window, up):
        self._window = window
        self._camera_pos = np.array((0.4, 0.5, 2.0))
        self._lookat_pos = np.array((0.0, 0.0, 0.0))
        self._up = np_normalize(np.array(up))
        self._last_mouse_pos = None

        self._auto_rotate = True
        self._spp = 0
        self._last_spp = 0
        self._spp_manual = 0

    @property
    def mouse_exclusive_owner(self):
        return True

    def update_camera(self, time):
        self._spp = time
        res = self._update_by_wasd()
        res = self._update_by_mouse() or res
        return res

    def _update_by_mouse(self):
        win = self._window
        if not self.mouse_exclusive_owner or not win.is_pressed(ti.ui.LMB):
            self._last_mouse_pos = None
            return False
        mouse_pos = np.array(win.get_cursor_pos())
        if self._last_mouse_pos is None:
            self._last_mouse_pos = mouse_pos
            return False
        # Makes camera rotation feels right
        dx, dy = self._last_mouse_pos - mouse_pos
        self._last_mouse_pos = mouse_pos

        out_dir = self._lookat_pos - self._camera_pos
        leftdir = self._compute_left_dir(np_normalize(out_dir))

        scale = 3
        rotx = np_rotate_matrix(self._up, dx * scale)
        roty = np_rotate_matrix(leftdir, dy * scale)

        out_dir_homo = np.array(list(out_dir) + [0.0])
        new_out_dir = np.matmul(np.matmul(roty, rotx), out_dir_homo)[:3]
        self._lookat_pos = self._camera_pos + new_out_dir

        return True

    def _update_by_wasd(self):
        win = self._window
        tgtdir = self.target_dir
        leftdir = self._compute_left_dir(tgtdir)
        lut = [
            ('w', tgtdir),
            ('a', leftdir),
            ('s', -tgtdir),
            ('d', -leftdir),
            ('e', [0, -1, 0]),
            ('q', [0, 1, 0]),
        ]
        dir = np.array([0.0, 0.0, 0.0])
        pressed = False
        for key, d in lut:
            if win.is_pressed(key):
                pressed = True
                dir += np.array(d)
        # custom
        if win.is_pressed('t'):
            self._auto_rotate = not self._auto_rotate

        if self._auto_rotate:
            if self._spp -self._last_spp > 0.25:
                self._last_spp = self._spp
                self._lookat_pos = np.array([0.0, 0.2, 0.0])
                x = 0.20
                z = 1.0
                theta = 0.1 * self._spp
                xx = x * math.cos(theta) + z * math.sin(theta)
                zz = -x * math.sin(theta) + z * math.cos(theta)
                self._camera_pos = np.array([xx, 0.4, zz]) * 4.0
                return True
            else:
                return False

        if win.is_pressed('m'):
            pressed = True
            self._spp_manual += 0.25
            self._lookat_pos = np.array([0.0, 0.2, 0.0])
            x = 0.20
            z = 1.0
            theta = 0.1 * self._spp_manual
            xx = x * math.cos(theta) + z * math.sin(theta)
            zz = -x * math.sin(theta) + z * math.cos(theta)
            self._camera_pos = np.array([xx, 0.4, zz]) * 4.0
            return True

        if win.is_pressed('b'):
            pressed = True
            self._lookat_pos = np.array([0.0, 0.2, 0.0])
            self._camera_pos = np.array([0.20, 0.4, 1.0]) * 4.0
            return True
        elif win.is_pressed('n'):
            pressed = True
            self._lookat_pos = np.array([0.0, 0.2, 0.0])
            self._camera_pos = np.array([-0.20, 0.4, -1.0]) * 4.0
            return True
        if not pressed:
            return False
        dir *= 0.05
        self._lookat_pos += dir
        self._camera_pos += dir
        return True

    @property
    def position(self):
        return self._camera_pos

    @property
    def look_at(self):
        return self._lookat_pos

    @property
    def target_dir(self):
        return np_normalize(self.look_at - self.position)

    def _compute_left_dir(self, tgtdir):
        cos = np.dot(self._up, tgtdir)
        if abs(cos) > 0.999:
            return np.array([-1.0, 0.0, 0.0])
        return np.cross(self._up, tgtdir)


class Scene:
    def __init__(self, voxel_edges=0.06, exposure=3):
        ti.init(arch=ti.vulkan)
        # ti.init(arch=ti.gpu)
        print(HELP_MSG)
        self.window = ti.ui.Window("Taichi Voxel Renderer",
                                   SCREEN_RES,
                                   vsync=True)
        self.camera = Camera(self.window, up=UP_DIR)
        self.renderer = Renderer(dx=VOXEL_DX,
                                 image_res=SCREEN_RES,
                                 up=UP_DIR,
                                 voxel_edges=voxel_edges,
                                 exposure=exposure)

        self.renderer.set_camera_pos(*self.camera.position)
        if not os.path.exists('screenshot'):
            os.makedirs('screenshot')

    @staticmethod
    @ti.func
    def round_idx(idx_):
        idx = ti.cast(idx_, ti.f32)
        return ti.Vector(
            [ti.round(idx[0]),
             ti.round(idx[1]),
             ti.round(idx[2])]).cast(ti.i32)

    @ti.func
    def set_voxel(self, idx, mat, color):
        self.renderer.set_voxel(self.round_idx(idx), mat, color)

    @ti.func
    def get_voxel(self, idx):
        mat, color = self.renderer.get_voxel(self.round_idx(idx))
        return mat, color

    def set_floor(self, height, color):
        self.renderer.floor_height[None] = height
        self.renderer.floor_color[None] = color

    def set_directional_light(self, direction, direction_noise, color):
        self.renderer.set_directional_light(direction, direction_noise, color)

    def set_background_color(self, color):
        self.renderer.background_color[None] = color

    def finish(self):
        self.renderer.recompute_bbox()
        canvas = self.window.get_canvas()
        spp = 1
        while self.window.running:
            should_reset_framebuffer = False

            if self.camera.update_camera(time.time()):
                self.renderer.set_camera_pos(*self.camera.position)
                look_at = self.camera.look_at
                self.renderer.set_look_at(*look_at)
                should_reset_framebuffer = True

            if should_reset_framebuffer:
                self.renderer.reset_framebuffer()

            t = time.time()
            for _ in range(spp):
                self.renderer.accumulate()
            img = self.renderer.fetch_image()
            if self.window.is_pressed('p'):
                timestamp = datetime.today().strftime('%Y-%m-%d-%H%M%S')
                dirpath = os.getcwd()
                main_filename = os.path.split(__main__.__file__)[1]
                fname = os.path.join(dirpath, 'screenshot', f"{main_filename}-{timestamp}.jpg")
                ti.tools.image.imwrite(img, fname)
                print(f"Screenshot has been saved to {fname}")
            canvas.set_image(img)
            elapsed_time = time.time() - t
            if elapsed_time * TARGET_FPS > 1:
                spp = int(spp / (elapsed_time * TARGET_FPS) - 1)
                spp = max(spp, 1)
            else:
                spp += 1
            self.window.show()
