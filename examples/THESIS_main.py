from horloadist import (
    KX,
    KY,
    XYSupportNode,
    ZSupportNode,
    Polygon,
    Polygons,
    Stucture,
    Load,
    LinSolve,
    ZLinSolve,
    loadvec
)


kx1 = KX.constRectangular(glo_dx=5.26, glo_dy=0.20)
ky1 = KY.constRectangular(glo_dx=5.26, glo_dy=0.20)

kx2 = KX.constRectangular(glo_dx=3.70, glo_dy=0.20)
ky2 = KY.constRectangular(glo_dx=3.70, glo_dy=0.20)

kx3 = KX.constRectangular(glo_dx=0.20, glo_dy=2.00)
ky3 = KY.constRectangular(glo_dx=0.20, glo_dy=2.00)

kx4_5 = KX.constRectangular(glo_dx=0.20, glo_dy=1.75)
ky4_5 = KY.constRectangular(glo_dx=0.20, glo_dy=1.75)

kx6_7 = KX.constRectangular(glo_dx=0.20, glo_dy=1.90)
ky6_7 = KY.constRectangular(glo_dx=0.20, glo_dy=1.90)


w1 = XYSupportNode(nr=1, glo_x=14.120, glo_y= 0.100, glo_kx=kx1, glo_ky=ky1)
w2 = XYSupportNode(nr=2, glo_x=14.900, glo_y=15.440, glo_kx=kx2, glo_ky=ky2)
w3 = XYSupportNode(nr=3, glo_x= 5.000, glo_y= 7.770, glo_kx=kx3, glo_ky=ky2)
w4 = XYSupportNode(nr=4, glo_x= 6.950, glo_y= 6.045, glo_kx=kx4_5, glo_ky=ky4_5)
w5 = XYSupportNode(nr=5, glo_x= 6.950, glo_y= 9.495, glo_kx=kx4_5, glo_ky=ky4_5)
w6 = XYSupportNode(nr=6, glo_x=11.490, glo_y= 6.070, glo_kx=kx6_7, glo_ky=ky6_7)
w7 = XYSupportNode(nr=7, glo_x=11.490, glo_y= 9.470, glo_kx=kx6_7, glo_ky=ky6_7)
xy_nodes = [w1, w2, w3, w4, w5, w6, w7]

s1 = ZSupportNode(nr= 8, glo_x= 0.100, glo_y= 0.100)
s2 = ZSupportNode(nr= 9, glo_x= 6.950, glo_y= 0.100)
s3 = ZSupportNode(nr=10, glo_x=16.650, glo_y= 5.210)
s4 = ZSupportNode(nr=11, glo_x=16.650, glo_y=10.330)
s5 = ZSupportNode(nr=12, glo_x= 6.950, glo_y=15.440)
s6 = ZSupportNode(nr=13, glo_x= 0.100, glo_y=15.440)
s7 = ZSupportNode(nr=14, glo_x= 0.100, glo_y=10.330)
s8 = ZSupportNode(nr=15, glo_x= 0.100, glo_y= 5.210)
z_nodes = [s1, s2, s3, s4, s5, s6, s7, s8]


# shell
pos_poly = Polygon([[0.000, 0.000], [16.750, 0.000], [16.750, 15.540], [0.000, 15.540]])

# openings
neg_poly1 = Polygon([[5.100, 6.970], [ 6.850, 6.970], [ 6.850,  8.570], [5.100, 8.570]])
neg_poly2 = Polygon([[8.420, 6.521], [11.390, 6.521], [11.390,  9.020], [8.420, 9.020]])

# all polygons together
tot_polygon = Polygons(pos_polygon=pos_poly, neg_polygons=[neg_poly1, neg_poly2])

struc = Stucture(xynodes=xy_nodes, glo_mass_centre=tot_polygon.centroid)

loadcase_x  = Load(x_magnitude=1, y_magnitude=0)

sol = LinSolve(xy_structure=struc, xy_load=loadcase_x)

# updates solution with vertical load results
# sol.to_rfem(polygon=tot_polygon, z_nodes=z_nodes, z_load_magnitude=1.00)

sol.printTable()

# # sol.to_mpl(tot_polygon, fname='example_to_mpl', show=False, save=True, fformat='png')


# # analyzing it pseudo vertical
# import pickle
# import os

# with open(os.path.join('example_vload_from_rfem','THESIS_main.pkl'), 'rb') as file:
#     vert_sol:LinSolve = pickle.load(file)


z_space = loadvec.z_linspace(z_num_floors=10, floor_heigt=2.50)

f_x_vec = loadvec.weighted_norm_g_by_polygon(
    z_space,
    S=1.0,
    polygon=tot_polygon,
    thickness=0.15,
    density=25.0
    )

# f_x_vec = loadvec.uniform(z_space=z_space, const_force=1000.0)

f_y_vec = loadvec.uniform(z_space=z_space, const_force=0.0)

zsol = ZLinSolve(
    linsolve=sol,
    z_space=z_space,
    f_x_vec=f_x_vec,
    f_y_vec=f_y_vec
)

zsol.to_rfem(tot_polygon, zload=1.0)

# zsol.to_plotly(
#     tot_fx_scale=10e-4,
#     tot_fy_scale=10e-4,
#     fx_scale=10e-4,
#     fy_scale=10e-4,
#     fz_scale=10e-2/2,
#     vx_scale=10e-4,
#     vy_scale=10e-4,
#     vz_scale=10e-2/2,
#     mx_scale=10e-4/3,
#     my_scale=10e-4/3,
#     polygon=tot_polygon
#     )