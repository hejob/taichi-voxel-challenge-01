from scene_custom import Scene # from scene import Scene
import taichi as ti
from taichi.math import *

n=64; scene=Scene(voxel_edges=0.02,exposure=2); scene.set_background_color(vec3(62.0,246.0,251.0)/255.0)
scene.set_floor(-20,vec3(94.0,251.0,57.0)/255.0); scene.set_directional_light((1,.2,.3),.1,vec3(1,1,1)/1.05)

@ti.func
def draw_base(c):
    ms = [vec3(1,0,1),vec3(-1,0,1),vec3(1,0,-1),vec3(-1,0,-1)]
    for i, j in ti.ndrange(n, n):
        mat = 2 if (min(i, j) == 0 or max(i, j) == n - 1) else 1
        for mi in ti.static(range(4)): scene.set_voxel(vec3(i*ms[mi][0],0*ms[mi][1],j*ms[mi][2]),mat,c)

@ti.func
def draw_poles(p, h):
    for mi, mj in ti.static([(1,1),(-1,1),(1,-1),(-1,-1)]):
        for k in range(h): scene.set_voxel(vec3(int(n*p[0]*mi),k,int(n*p[1]*mj)),1,vec3(142.0,125.0,13.0)/255.0)

@ti.func
def p_to_x(p): return p * 2.0 * n
@ti.func
def x_to_p(x): return x / 2.0 / n
@ti.func
def x_to_I(x): return int(x) # is this good for negative floats?
@ti.func
def I_to_x(I): return I + 0.5
@ti.func
def interp_line(I1, I2, i, J1, J2): return J1 if I2==I1 else x_to_I(I_to_x(J1) + float(J2 - J1) * (i - I1) / (I2 - I1))

@ti.func
def draw_iparallel_rect(ps, c, fillh, bottom):  # p0-p1 // p2-p3 (parallel edges)
    IJKs = [x_to_I(p_to_x(p)) for p in ps]
    I1, I2, Jb = IJKs[0][0], IJKs[2][0], x_to_I(p_to_x(bottom)) if fillh == 1 else 0
    for i in ti.ndrange((I1, I2+1),):
        K1, K2 = interp_line(I1, I2, i, IJKs[0][2], IJKs[2][2]), interp_line(I1, I2, i, IJKs[1][2], IJKs[3][2])
        for k in ti.ndrange((K1, K2+1),):
            j1, j2 = interp_line(I1, I2, i, IJKs[0][1], IJKs[2][1]), interp_line(I1, I2, i, IJKs[1][1], IJKs[3][1])
            J = interp_line(K1, K2, k, j1, j2)
            if fillh == 1:
                for j in ti.ndrange((Jb, J+1),): scene.set_voxel(vec3(i, j, k), 1, c)
            else: scene.set_voxel(vec3(i, J, k), 1, c)

@ti.func
def draw_roof(scale, h, shiftz, c):
    verts_origin=[(-.5,-.1443,-.75),(-.2513,.051,-.75),(-.142,.0,-1.14),(.25,.05,-.75),
    (.5,-.15,-.75),(-.5,-.1443,.75),(-.2513,.051,.75),(-.142,.0,.353),(.25,.05,.75),(.5,-.15,0.75)]
    vs = [vec3(0, h, shiftz) + scale * vec3(x, y, z) for (x, y, z) in verts_origin]
    for ind in ti.static(range(4)): draw_iparallel_rect([vs[0+ind], vs[5+ind], vs[1+ind], vs[6+ind]], c, 0, 0.0)

@ti.func
def draw_wheel(yc, zc, r, x0, x1, c):
    I0, I1, J0, J1 = x_to_I(p_to_x(x0)), x_to_I(p_to_x(x1)), x_to_I(p_to_x(yc - r)), x_to_I(p_to_x(yc + r))
    K0, K1 = x_to_I(p_to_x(zc - r)), x_to_I(p_to_x(zc + r))
    radius, yc_x, zc_x = p_to_x(r), p_to_x(yc), p_to_x(zc)
    for i in ti.ndrange((I0, I1+1),):
        for j in ti.ndrange((J0, J1+1),):
            for k in ti.ndrange((K0, K1+1),):
                y_x, z_x = I_to_x(j), I_to_x(k)
                if (y_x-yc_x)**2+(z_x-zc_x)**2<=0.25*radius**2: scene.set_voxel(vec3(i, j, k), 1, 255.0-c)
                elif (y_x-yc_x)**2+(z_x-zc_x)**2<=radius**2: scene.set_voxel(vec3(i, j, k), 1, c)

@ti.func
def draw_window(v1, v2, v3, v4, c): # scale = 0.8
    vc = (v1 + v2 + v3 + v4) * 0.25
    vs = [(vc + 0.8 * (v - vc)) for v in [v1, v2, v3, v4]]
    draw_iparallel_rect([vs[0], vs[1], vs[2], vs[3]], c, 1, 0.1)

@ti.func
def draw_car(scale, h, shiftz, c):
    verts_origin = [(-.2032,.3021,-.5),(-.2032,.5124,-.3516),(-.2032,.5124,.11),(-.2032,.32,.27),
    (-.2032,.24,.5),(.2032,.3021,-.5),(.2032,.5124,-.3516),(.2032,.5124,.11),(.2032,.32,.27),(.2032,.24,.5)]
    hl, vs = h + scale * 0.1201, [vec3(0, h, shiftz) + scale * vec3(x, y, z) for (x, y, z) in verts_origin]
    for ind in ti.static(range(4)): draw_iparallel_rect([vs[0+ind], vs[1+ind], vs[5+ind], vs[6+ind]], c, 1, hl)
    w1, w2, wr, ww = scale * 0.2014, scale * 0.7933, 0.7 * scale * 0.1201, scale * 0.0353
    draw_wheel(hl, vs[0][2] + w1, wr, vs[0][0], vs[0][0] + ww, vec3(0.0, 0.0, 0.0))
    draw_wheel(hl, vs[0][2] + w2, wr, vs[0][0], vs[0][0] + ww, vec3(0.0, 0.0, 0.0))
    draw_wheel(hl, vs[0][2] + w1, wr, vs[5][0] - ww, vs[5][0], vec3(0.0, 0.0, 0.0))
    draw_wheel(hl, vs[0][2] + w2, wr, vs[5][0] - ww, vs[5][0], vec3(0.0, 0.0, 0.0))
    draw_window(vs[2],vs[3],vs[7],vs[8],vec3(1.,1.,1.)/255.); draw_window(vs[0],vs[1],vs[5],vs[6],vec3(1.,1.,1.)/255.)
    # draw_window(vs[0],vs[3],vs[1],vs[2],vec3(1.,1.,1.)/255.)

@ti.kernel
def initialize_voxels():
    draw_base(vec3(190.0, 190.0, 228.0) / 255.0)
    draw_poles((0.25, 0.35), 48)
    draw_roof(0.45, 0.37, 0.1, vec3(225.0, 225.0, 225.0) / 255.0)
    draw_car(0.45, 0.0, 0.0, vec3(200.0, 200.0, 93.0) / 255.0)

initialize_voxels()
scene.finish()
