# from scene import Scene
from scene_custom import Scene
import taichi as ti
from taichi.math import *

exposure = 10
scene = Scene(voxel_edges=1, exposure=exposure) # voxel_edges=10, 
# scene.set_floor(-0.05, (1.0, 1.0, 1.0))
# scene.set_background_color((1.0, 0, 0))
scene.set_directional_light((1, 0.3, 0.4), 0.1, vec3(1, 1, 1) / exposure)
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
        scene.set_voxel(vec3(i, k, j), 1, vec3(119.0, 123.0, 106.0) / 255.0)

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
def draw_ipar_rectangle(ps, c, fillh, bottom):  # p0-p1 // p2-p3 (parallel edges)
    IJKs = [x_to_I(p_to_x(p)) for p in ps]
    print('IJKs')
    print(IJKs)
    I1 = IJKs[0][0]
    I2 = IJKs[2][0]

    Jb = 0
    if fillh == 1:
        Jb = x_to_I(p_to_x(bottom))

    for i in ti.ndrange((I1, I2+1),):
        K1 = interp_line(I1, I2, i, IJKs[0][2], IJKs[2][2])
        K2 = interp_line(I1, I2, i, IJKs[1][2], IJKs[3][2])

        print(i, IJKs[0][2], IJKs[2][2], K1)
        print(i, IJKs[1][2], IJKs[3][2], K2)
        for k in ti.ndrange((K1, K2+1),):
            # J = interp_line(I1, I2, i, IJKs[0][1], IJKs[2][1])
            j1 = interp_line(I1, I2, i, IJKs[0][1], IJKs[2][1]) # TODO: use float here
            j2 = interp_line(I1, I2, i, IJKs[1][1], IJKs[3][1])
            J = interp_line(K1, K2, k, j1, j2)
            print(i, IJKs[0][1], IJKs[2][1], J)
            if fillh == 1:
                for j in ti.ndrange((Jb, J+1),):
                    scene.set_voxel(vec3(i, j, k), 1, c)
            else:
                scene.set_voxel(vec3(i, J, k), 1, c)

@ti.func
def draw_roof(scale, h, shiftz):
    c = vec3(225.0, 225.0, 225.0) / 255.0
    verts_origin = [(-0.5, -0.14432601728869932, -0.7483714140597398), (-0.25125243421038385, 0.050526242579833354, -0.7483714140597398), (-0.14177890862074488, 0.0, -1.1433452159246025), (0.2500152670884, 0.0500162777501036, -0.7483714140597398), (0.5, -0.14997150857917646, -0.7483714140597398), (-0.5, -0.14432601728869932, 0.7483714140597398), (-0.25125243421038385, 0.050526242579833354, 0.7483714140597398), (-0.14177890862074488, 0.0, 0.35339761219487714), (0.2500152670884, 0.0500162777501036, 0.7483714140597398), (0.5, -0.14997150857917646, 0.7483714140597398)]
    vs = [vec3(0, h, shiftz) + scale * vec3(x, y, z) for (x, y, z) in verts_origin]
    draw_ipar_rectangle([vs[0], vs[5], vs[1], vs[6]], c, 0, 0.0)
    draw_ipar_rectangle([vs[1], vs[6], vs[2], vs[7]], c, 0, 0.0)
    draw_ipar_rectangle([vs[2], vs[7], vs[3], vs[8]], c, 0, 0.0)
    draw_ipar_rectangle([vs[3], vs[8], vs[4], vs[9]], c, 0, 0.0)

@ti.func
def draw_wheel(yc, zc, r, x0, x1):
    print('wheel')
    print(yc, zc, r, x0, x1)
    c = vec3(1.0, 0.0, 0.0)

    I0 = x_to_I(p_to_x(x0))
    I1 = x_to_I(p_to_x(x1))
    J0 = x_to_I(p_to_x(yc - r))
    J1 = x_to_I(p_to_x(yc + r))
    K0 = x_to_I(p_to_x(zc - r))
    K1 = x_to_I(p_to_x(zc + r))
    radius = p_to_x(r)
    yc_x = p_to_x(yc)
    zc_x = p_to_x(zc)
    for i in ti.ndrange((I0, I1+1),):
        for j in ti.ndrange((J0, J1+1),):
            for k in ti.ndrange((K0, K1+1),):
                y_x = I_to_x(j)
                z_x = I_to_x(k)
                if (y_x-yc_x)*(y_x-yc_x)+(z_x-zc_x)*(z_x-zc_x) <= radius*radius:
                    scene.set_voxel(vec3(i, j, k), 2, c)

@ti.func
def draw_window(v1, v2, v3, v4, c):
    scale = 0.8 # shrink according to center
    vc = (v1 + v2 + v3 + v4) * 0.25
    vs = [(vc + scale * (v - vc)) for v in [v1, v2, v3, v4]]
    draw_ipar_rectangle([vs[0], vs[1], vs[2], vs[3]], c, 2, 0.0)

@ti.func
def draw_car(scale, h, shiftz):
    c = vec3(200.0, 200.0, 93.0) / 255.0

    verts_origin = [(-0.20318021201413428, 0.30212014134275617, -0.5), (-0.20318021201413428, 0.5123674911660777, -0.35159010600706714), (-0.20318021201413428, 0.5123674911660777, 0.08833922261484099), (-0.20318021201413428, 0.3745583038869258, 0.22791519434628976), (-0.20318021201413428, 0.31802120141342755, 0.5), (0.20318021201413428, 0.30212014134275617, -0.5), (0.20318021201413428, 0.5123674911660777, -0.35159010600706714), (0.20318021201413428, 0.5123674911660777, 0.08833922261484099), (0.20318021201413428, 0.3745583038869258, 0.22791519434628976), (0.20318021201413428, 0.31802120141342755, 0.5)]
    hl_origin = 0.12014134275618374

    vs = [vec3(0, h, shiftz) + scale * vec3(x, y, z) for (x, y, z) in verts_origin]
    hl = h + scale * hl_origin
    print(vs)
    draw_ipar_rectangle([vs[0], vs[1], vs[5], vs[6]], c, 1, hl)
    draw_ipar_rectangle([vs[1], vs[2], vs[6], vs[7]], c, 1, hl)
    draw_ipar_rectangle([vs[2], vs[3], vs[7], vs[8]], c, 1, hl)
    draw_ipar_rectangle([vs[3], vs[4], vs[8], vs[9]], c, 1, hl)

    w1, w2 = scale * 0.20141342756183744, scale * 0.7932862190812721
    wr, ww = 0.7 * scale * 0.12014134275618374, scale * 0.0353356890459364
    # draw_wheel(yc, zc, wr_x, x0, x1)
    print(w1, w2, wr, ww, vs)
    draw_wheel(hl, vs[0][2] + w1, wr, vs[0][0], vs[0][0] + ww)
    draw_wheel(hl, vs[0][2] + w2, wr, vs[0][0], vs[0][0] + ww)
    draw_wheel(hl, vs[0][2] + w1, wr, vs[5][0] - ww, vs[5][0])
    draw_wheel(hl, vs[0][2] + w2, wr, vs[5][0] - ww, vs[5][0])

    draw_window(vs[2], vs[3], vs[7], vs[8], vec3(0.0, 0.0, 0.0) / 255.0)
    draw_window(vs[0], vs[1], vs[5], vs[6], vec3(0.0, 0.0, 0.0) / 255.0)

@ti.kernel
def initialize_voxels():
    draw_base()

    draw_pole((0.25, 0.3), 47)
    draw_pole((-0.25, 0.3), 47)
    draw_pole((0.25, -0.3), 47)
    draw_pole((-0.25, -0.3), 47)

    draw_roof(0.45, 0.37, 0.1)
    draw_car(0.45, 0.0, 0.0)


initialize_voxels()

ti.sync()

scene.finish()
