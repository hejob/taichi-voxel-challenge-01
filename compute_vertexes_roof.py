import math
# Vertexs_2D_ScanCoords =
# 	-105 0
# 	-29  0
# 	0    -95
# 	95   0
# 	172  0
# 	-105 360
# 	-29  360
# 	0    265
# 	95   360
# 	172  360

# Characteristic Coord Lengths
L1 = 76.0
L2 = 29.0
L3 = 95.0
L4 = 77.0
H1 = 360.0
H2 = 95.0

# 2D Coords Reconstruction
p1 = (-(L1+L2), 0.0, 0.0)
p2 = (-L2, 0.0, 0.0)
p3 = (0.0, 0.0, -H2)
p4 = (L3, 0, 0)
p5 = (L3+L4, 0, 0)
# p6~20 = p1~5 + (0, H1, 0)


# ang raw data by support bridge's parts
# a0 = (330, 452)
# b0 = (390, 499)
# c0 = (416, 487)
# d0 = (510, 499)
# d1 = (570, 451)
slopeA = (60, 47)
slopeB = (26, 12)
slopeC = (94, 12)
slopeD = (60, 48)

alfa = math.atan(47.0 / 60.0)
alfb = math.atan(12.0 / 26.0)
alfc = math.atan(12.0 / 94.0)
alfd = math.atan(48.0 / 60.0)

# 2D rotated points
PI = 3.1415926
# alfs = [a / 180.0 * PI for a in [-40.0, -5.0, 40.0, 30.0]]
alfs = [-alfb, -alfc, alfa, alfd]

def add_vec(a, b):
	# assert len(a) == len(b)
	return tuple([a[i] + b[i] for i in range(len(a))])

cossins = [(math.cos(a), math.sin(a)) for a in alfs]
P3 = p3
P2 = (-L2 * cossins[0][0], -L2 * cossins[0][1], 0.0)
P4 = (L3 * cossins[1][0], -L3 * cossins[1][1], 0.0)
P1 = add_vec(P2, (-L1 * cossins[2][0], -L1 * cossins[2][1], 0.0))
P5 = add_vec(P4, (L4 * cossins[3][0], -L4 * cossins[3][1], 0.0))

P6 = add_vec(P1, (0.0, 0.0, H1))
P7 = add_vec(P2, (0.0, 0.0, H1))
P8 = add_vec(P3, (0.0, 0.0, H1))
P9 = add_vec(P4, (0.0, 0.0, H1))
P10 = add_vec(P5, (0.0, 0.0, H1))

# center shift and scaled by X-dir width
dx = P5[0] - P1[0]
Pcx = (P1[0] + P5[0]) / 2.0
Pcz = (P1[2] + P6[2]) / 2.0

def scale_vec(v):
	return ((v[0] - Pcx) / dx, v[1] / dx, (v[2] - Pcz) / dx)

normalizedPoints = [scale_vec(v) for v in [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]]

print(str(normalizedPoints))

# rotation by 180 deg, bottom-up
def rotate_bottomup(v):
	x, y, z = v[0], v[1], v[2]
	return (x, -y, -z)

rotatedNormalizedPoints = [rotate_bottomup(v) for v in normalizedPoints]
# ??
# print(str(rotatedNormalizedPoints))
