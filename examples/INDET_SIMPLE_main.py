from horloadist import KX, KY, Polygon, SupportNode, Stucture, LinSolve

kx1 = KX.constRectangular(dx_glob=3.00, dy_glob=0.30)
ky1 = KY.constRectangular(dx_glob=3.00, dy_glob=0.30)

kx2 = KX.constRectangular(dx_glob=0.30, dy_glob=2.00)
ky2 = KY.constRectangular(dx_glob=0.30, dy_glob=2.00)

kx3 = KX.constRectangular(dx_glob=2.00, dy_glob=0.30)
ky3 = KY.constRectangular(dx_glob=2.00, dy_glob=0.30)

kx4 = KX.constRectangular(dx_glob=0.30, dy_glob=3.00)
ky4 = KY.constRectangular(dx_glob=0.30, dy_glob=3.00)


w1 = SupportNode(nr=1, glob_x=3.50, glob_y=0.00, glob_kx=kx1, glob_ky=ky1)
w2 = SupportNode(nr=2, glob_x=7.00, glob_y=4.00, glob_kx=kx2, glob_ky=ky2)
w3 = SupportNode(nr=3, glob_x=6.00, glob_y=5.00, glob_kx=kx3, glob_ky=ky3)
w4 = SupportNode(nr=4, glob_x=2.00, glob_y=4.00, glob_kx=kx4, glob_ky=ky4)


poly = Polygon([[0, 0], [7, 0], [7, 4], [0, 4]])

s1 = Stucture(nodes=[w1, w2, w3, w4], glo_mass_centre=poly.centroid)

s1.printTable()

ls1 = LinSolve(s1, x_mass_force=1, y_mass_force=1)

ls1.printTable()
