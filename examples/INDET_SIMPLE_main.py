from horloadist import KX, KY, Polygon, SupportNode, Stucture, LinSolve, XYLoad

kx1 = KX.constRectangular(glo_dx=3.00, glo_dy=0.30)
ky1 = KY.constRectangular(glo_dx=3.00, glo_dy=0.30)

kx2 = KX.constRectangular(glo_dx=0.30, glo_dy=2.00)
ky2 = KY.constRectangular(glo_dx=0.30, glo_dy=2.00)

kx3 = KX.constRectangular(glo_dx=2.00, glo_dy=0.30)
ky3 = KY.constRectangular(glo_dx=2.00, glo_dy=0.30)

kx4 = KX.constRectangular(glo_dx=0.30, glo_dy=3.00)
ky4 = KY.constRectangular(glo_dx=0.30, glo_dy=3.00)


w1 = SupportNode(nr=1, glo_x=3.50, glo_y=0.00, glo_kx=kx1, glo_ky=ky1)
w2 = SupportNode(nr=2, glo_x=7.00, glo_y=4.00, glo_kx=kx2, glo_ky=ky2)
w3 = SupportNode(nr=3, glo_x=6.00, glo_y=5.00, glo_kx=kx3, glo_ky=ky3)
w4 = SupportNode(nr=4, glo_x=2.00, glo_y=4.00, glo_kx=kx4, glo_ky=ky4)

poly = Polygon([[0, 0], [7, 0], [7, 5], [0, 5]])

s1 = Stucture(nodes=[w1, w2, w3, w4], glo_mass_centre=poly.centroid)

# s1.printTable()

load = XYLoad(x_magnitude=1, y_magnitude=1)

ls1 = LinSolve(structure=s1, load=load)

# # ls1.to_rfem(poly) # let rfem calculate (windows only)

ls1.to_ops()

# # ls1.to_mpl(poly, save=False, fformat='png')

# ls1.printTable()




# # different coordinate system

# print('\n=========== changed coord system ===========\n')

# dx, dy = -3.50, -2.00

# poly = Polygon([[0+dx, 0+dy], [7+dx, 0+dy], [7+dx, 5+dy], [0+dx, 5+dy]])

# w1 = SupportNode(nr=1, glo_x=3.50+dx, glo_y=0.00+dy, glo_kx=kx1, glo_ky=ky1)
# w2 = SupportNode(nr=2, glo_x=7.00+dx, glo_y=4.00+dy, glo_kx=kx2, glo_ky=ky2)
# w3 = SupportNode(nr=3, glo_x=6.00+dx, glo_y=5.00+dy, glo_kx=kx3, glo_ky=ky3)
# w4 = SupportNode(nr=4, glo_x=2.00+dx, glo_y=4.00+dy, glo_kx=kx4, glo_ky=ky4)

# s1 = Stucture(nodes=[w1, w2, w3, w4], glo_mass_centre=poly.centroid)

# s1.printTable()

# ls1 = LinSolve(structure=s1, load=load)

# ls1.printTable()

