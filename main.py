# from scene import Scene
from scene_custom import Scene
import taichi as ti
from taichi.math import *

exposure = 20
scene = Scene(voxel_edges=1, exposure=exposure) # voxel_edges=10, 
# scene.set_floor(-0.05, (1.0, 1.0, 1.0))
# scene.set_background_color((1.0, 0, 0))
scene.set_directional_light((1, 1, 1), 0.1, vec3(1, 1, 1) / exposure)
scene.set_background_color(vec3(0.3, 0.4, 0.6) / exposure)

n = 64

@ti.func
def draw_base():
    # for I in ti.grouped(ti.ndrange((0, n), (0, 1), (0, n))):
    #     scene.set_voxel(I, 2, )
    for i, j in ti.ndrange(n, n):
        c = vec3(180.0, 180.0, 192.0) / 255.0
        if min(i, j) == 0 or max(i, j) == n - 1:
            scene.set_voxel(vec3(i, 0, j), 2, c)
            scene.set_voxel(vec3(-i, 0, j), 2, c)
            scene.set_voxel(vec3(i, 0, -j), 2, c)
            scene.set_voxel(vec3(-i, 0, -j), 2, c)
        else:
            scene.set_voxel(vec3(i, 0, j), 1, c)
            scene.set_voxel(vec3(-i, 0, j), 1, c)
            scene.set_voxel(vec3(i, 0, -j), 1, c)
            scene.set_voxel(vec3(-i, 0, -j), 1, c)

@ti.func
def draw_pole(pos, h):
    i, j = int(n * pos[0]), int(n * pos[1])
    for k in range(h):
        scene.set_voxel(vec3(i, k, j), 2, vec3(119.0, 123.0, 106.0) / 255.0)

@ti.func
def p_to_x(p):
    return p * 2.0 * n

@ti.func
def x_to_p(x):
    return x / 2.0 / n

@ti.func
def x_to_I(x):
    return int(x) # is this good for negative floats?

@ti.func
def I_to_x(I):
    return I + 0.5

@ti.func
def interp_line(I1, I2, i, J1, J2):  # integers
    yj = I_to_x(J1) + float(J2 - J1) * (i - I1) / (I2 - I1)
    return x_to_I(yj)

@ti.func
def draw_ipar_rectangle(ps, c):  # p0-p1 // p2-p3 (parallel edges)
    IJKs = [x_to_I(p_to_x(p)) for p in ps]
    print('IJKs')
    print(IJKs)
    I1 = IJKs[0][0]
    I2 = IJKs[2][0]
    for i in ti.ndrange((I1, I2+1),):
        K1 = interp_line(I1, I2, i, IJKs[0][2], IJKs[2][2])
        K2 = interp_line(I1, I2, i, IJKs[1][2], IJKs[3][2])

        print(i, IJKs[0][2], IJKs[2][2], K1)
        print(i, IJKs[1][2], IJKs[3][2], K2)
        for k in ti.ndrange((K1, K2+1),):
            J = interp_line(I1, I2, i, IJKs[0][1], IJKs[2][1])
            print(i, IJKs[0][1], IJKs[2][1], J)
            scene.set_voxel(vec3(i, J, k), 2, c)

@ti.func
def draw_roof(scale, h, shiftz):
    c = vec3(225.0, 225.0, 225.0) / 255.0

    verts_origin = [(-0.5, -0.14432601728869932, -0.7483714140597398), (-0.25125243421038385, 0.050526242579833354, -0.7483714140597398), (-0.14177890862074488, 0.0, -1.1433452159246025), (0.2500152670884, 0.0500162777501036, -0.7483714140597398), (0.5, -0.14997150857917646, -0.7483714140597398), (-0.5, -0.14432601728869932, 0.7483714140597398), (-0.25125243421038385, 0.050526242579833354, 0.7483714140597398), (-0.14177890862074488, 0.0, 0.35339761219487714), (0.2500152670884, 0.0500162777501036, 0.7483714140597398), (0.5, -0.14997150857917646, 0.7483714140597398)]

    scale = 0.4

    vs = [vec3(0, h, shiftz) + scale * vec3(x, y, z) for (x, y, z) in verts_origin]
    # verts = [
    #     vec3(-0.5, 0.2, -0.6),
    #     vec3( 0.0, 0.4, -0.8),
    #     vec3( 0.2, 0.3, -0.6),
    #     vec3( 0.4, 0.3, -0.6),
    #     vec3( 0.5, 0.4, -0.6),

    #     vec3(-0.5, 0.2, 0.6),
    #     vec3( 0.0, 0.4, 0.4),
    #     vec3( 0.2, 0.3, 0.6),
    #     vec3( 0.4, 0.3, 0.6),
    #     vec3( 0.5, 0.4, 0.6),
    # ]
    # vs = [v * scale for v in verts]
    print(vs)
    draw_ipar_rectangle([vs[0], vs[5], vs[1], vs[6]], c)
    draw_ipar_rectangle([vs[1], vs[6], vs[2], vs[7]], c)
    draw_ipar_rectangle([vs[2], vs[7], vs[3], vs[8]], c)
    draw_ipar_rectangle([vs[3], vs[8], vs[4], vs[9]], c)
    # bottom-up rotated, order changed
    # draw_ipar_rectangle([vs[5], vs[0], vs[6], vs[1]], c)
    # draw_ipar_rectangle([vs[6], vs[1], vs[7], vs[2]], c)
    # draw_ipar_rectangle([vs[7], vs[2], vs[8], vs[3]], c)
    # draw_ipar_rectangle([vs[8], vs[3], vs[9], vs[4]], c)



@ti.kernel
def initialize_voxels():
    draw_base()

    draw_pole((0.25, 0.3), 52)
    draw_pole((-0.25, 0.3), 52)
    draw_pole((0.25, -0.3), 52)
    draw_pole((-0.25, -0.3), 52)

    draw_roof(0.5, 0.42, 0.1)


initialize_voxels()

ti.sync()

scene.finish()
