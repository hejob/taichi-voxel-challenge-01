import math
# Vertexs_2D_ScanCoords = # front to the right
# 91 173 (bottom back upper point)
# 175 54
# 424 54
# 503 132
# 657 164
#
# 91 278 (bottom back)
# 198 344  (wheel bottom, right rear)
# X 205 540 (2 wheels, back, front)

# Characteristic Points, Coord Lengths
pref00 = (91, 344)
p1 = (0, 171)
p2 = (84, 290)
p3 = (333, 290)
p4 = (412, 212)
p5 = (566, 180)

hl = 68
wx1 = 114
wx2 = 449
wr = 68
width = 230


# 2D Coords Reconstruction
def add_vec(a, b):
	# assert len(a) == len(b)
	return tuple([a[i] + b[i] for i in range(len(a))])

P1 = (0.0, p1[1], p1[0])
P2 = (0.0, p2[1], p2[0])
P3 = (0.0, p3[1], p3[0])
P4 = (0.0, p4[1], p4[0])
P5 = (0.0, p5[1], p5[0])

P6 = add_vec(P1, (width, 0.0, 0.0))
P7 = add_vec(P2, (width, 0.0, 0.0))
P8 = add_vec(P3, (width, 0.0, 0.0))
P9 = add_vec(P4, (width, 0.0, 0.0))
P10 = add_vec(P5, (width, 0.0, 0.0))

Hlow = float(hl)
Px1 = float(wx1)
Px2 = float(wx2)
Wr = float(wr)
Ww = 20.0

# center shift and scaled by X-dir width
dx = P5[2] - P1[2]
Pcx = width / 2.0
Pcz = (P1[2] + P5[2]) / 2.0

def scale_vec(v):
	return ((v[0] - Pcx) / dx, v[1] / dx, (v[2] - Pcz) / dx)

print('pts')
normalizedPoints = [scale_vec(v) for v in [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]]
print(str(normalizedPoints))

print('h')
print(str(Hlow / dx))

print('w1, w2')
print(str(Px1 / dx))
print(str(Px2 / dx))

print('wr')
print(str(Wr / dx))

print('ww')
print(str(Ww / dx))

# # rotation by 180 deg, bottom-up
# def rotate_bottomup(v):
# 	x, y, z = v[0], v[1], v[2]
# 	return (x, -y, -z)

# rotatedNormalizedPoints = [rotate_bottomup(v) for v in normalizedPoints]
# # ??
# # print(str(rotatedNormalizedPoints))
