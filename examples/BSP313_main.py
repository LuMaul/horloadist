from horloadist import KX, KY, XYSupportNode, Polygon, Stucture, LinSolve, Load


kx1 = KX.constRectangular(0.25, 4)
ky1 = KY.constRectangular(0.25, 4)

kx2 = KX.constRectangular(0.25, 6)
ky2 = KY.constRectangular(0.25, 6)

kx3 = KX.constRectangular(12, 0.25)
ky3 = KY.constRectangular(12, 0.25)

kx4 = KX.constRectangular(4, 0.25)
ky4 = KY.constRectangular(4, 0.25)


w1 = XYSupportNode(1, -8, 3.0, kx1, ky1)
w2 = XYSupportNode(2, -2, 2.0, kx2, ky2)
w3 = XYSupportNode(3,  2,-5.0, kx3, ky3)
w4 = XYSupportNode(4,  0, 5.0, kx4, ky4)


pl = Polygon([[8, 5], [8, -5], [-8, -5], [-8, 5]])


struc = Stucture(xynodes=[w1, w2, w3, w4], glo_mass_centre=pl.centroid)
struc.printTable()

load = Load(x_magnitude=1, y_magnitude=1)

sol = LinSolve(struc, load)
sol.printTable()

sol.to_mpl(pl, save=False)