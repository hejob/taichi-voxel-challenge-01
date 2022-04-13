from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(exposure=10)
scene.set_floor(-0.05, (1.0, 1.0, 1.0))
scene.set_direction_light((1, 0, 0), 0.1, color=(1, 1, 1))

@ti.kernel
def initialize_scene():
    n = 50
    for i, j in ti.ndrange(n, n):
        if min(i, j) == 0 or max(i, j) == n - 1:
            # scene.set_voxel(idx=(i, 0, j), mat=2, color=(0.9, 0.1, 0.1))
            # scene.set_voxel(idx=vec3(i, 0, j), mat=2, color=vec3(0.9, 0.1, 0.1))
            scene.set_voxel(vec3(i, 0, j), 2, vec3(0.9, 0.1, 0.1))
        else:
            scene.set_voxel(vec3(i, 0, j), 1, vec3(0.9, 0.1, 0.1))

            if ti.random() < 0.04:
                height = int(ti.random() * 20)

                for k in range(1, height):
                    scene.set_voxel(vec3(i, k, j), 1, vec3(0.0, 0.5, 0.9))
                if height:
                    scene.set_voxel(vec3(i, height, j), 2, vec3(1, 1, 1))

initialize_scene()

scene.finish()