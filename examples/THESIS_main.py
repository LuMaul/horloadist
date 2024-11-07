from horloadist import KX, KY, SupportNode, Polygon, Polygons, Stucture

kx1 = KX.constRectangular(glo_dx=5.26, glo_dy=0.20)
ky1 = KY.constRectangular(glo_dx=5.26, glo_dy=0.20)

kx2 = KX.constRectangular(glo_dx=3.70, glo_dy=0.20)
ky2 = KY.constRectangular(glo_dx=3.70, glo_dy=0.20)

kx3 = KX.constRectangular(glo_dx=0.20, glo_dy=2.00)
ky3 = KY.constRectangular(glo_dx=0.20, glo_dy=2.00)

kx4_5 = KX.constRectangular(glo_dx=0.20, glo_dy=1.65)
ky4_5 = KY.constRectangular(glo_dx=0.20, glo_dy=1.65)

kx6_7 = KX.constRectangular(glo_dx=0.20, glo_dy=1.90)
ky6_7 = KY.constRectangular(glo_dx=0.20, glo_dy=1.90)


w1 = SupportNode(nr=1, glo_x=14.120, glo_y= 0.100, glo_kx=kx1, glo_ky=ky1)
w2 = SupportNode(nr=2, glo_x=14.900, glo_y=15.440, glo_kx=kx2, glo_ky=ky2)
w3 = SupportNode(nr=3, glo_x= 5.000, glo_y= 7.770, glo_kx=kx3, glo_ky=ky2)
w4 = SupportNode(nr=4, glo_x= 6.950, glo_y= 6.045, glo_kx=kx4_5, glo_ky=ky4_5)
w5 = SupportNode(nr=5, glo_x= 6.950, glo_y= 9.495, glo_kx=kx4_5, glo_ky=ky4_5)
w6 = SupportNode(nr=6, glo_x=11.490, glo_y= 6.070, glo_kx=kx6_7, glo_ky=ky6_7)
w7 = SupportNode(nr=7, glo_x=11.490, glo_y= 9.470, glo_kx=kx6_7, glo_ky=ky6_7)

# shell
pos_poly1 = Polygon([[0.000, 0.000], [16.750, 0.000], [16.750, 15.540], [0.000, 15.540]])
# recesses
neg_poly1 = Polygon([[5.100, 6.970], [ 6.850, 6.970], [ 6.850,  8.570], [5.100, 8.570]])
neg_poly2 = Polygon([[8.420, 6.521], [11.390, 6.521], [11.390,  9.020], [8.420, 9.020]])

tot_polygon = Polygons(pos_polygons=[pos_poly1], neg_polygons=[neg_poly1, neg_poly2])


s1 = Stucture(nodes=[w1, w2, w3, w4, w5, w6, w7], glo_mass_centre=tot_polygon.centroid)

s1.to_mpl(polygon=tot_polygon)