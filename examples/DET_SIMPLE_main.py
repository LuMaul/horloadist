from horloadist import KX, KY, Polygon, XYSupportNode, Stucture, LinSolve, Load

# simple statically determined shell 5.00 x 5.00 m with walls left, below, right

kx1 = KX.constRectangular(glo_dx=0.30, glo_dy=5.00)
ky1 = KY.constRectangular(glo_dx=0.30, glo_dy=5.00)

kx2 = KX.constRectangular(glo_dx=0.30, glo_dy=5.00)
ky2 = KY.constRectangular(glo_dx=0.30, glo_dy=5.00)

kx3 = KX.constRectangular(glo_dx=5.00, glo_dy=0.30)
ky3 = KY.constRectangular(glo_dx=5.00, glo_dy=0.30)

n1 = XYSupportNode(nr=1, glo_x=0.00, glo_y=2.50, glo_kx=kx1, glo_ky=ky1)
n2 = XYSupportNode(nr=2, glo_x=5.00, glo_y=2.50, glo_kx=kx2, glo_ky=ky2)
n3 = XYSupportNode(nr=3, glo_x=2.50, glo_y=0.00, glo_kx=kx3, glo_ky=ky3)

struc = Stucture(xynodes=[n1, n2, n3], glo_mass_centre=(2.50, 2.50))

poly = Polygon(glob_xy=[[0, 0], [5, 0], [5, 5], [0, 5]])

struc.printTable()

load = Load(x_magnitude=1.00)

sol = LinSolve(xy_structure=struc, xy_load=load)

# sol.to_rfem(poly) # let rfem calculate (windows only)

sol.printTable()

sol.to_mpl(poly, f_disp_scale=1, save=False, forces='torsion')