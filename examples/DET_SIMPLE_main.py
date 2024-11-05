from horloadist import KX, KY, Polygon, SupportNode, Stucture, LinSolve, XYLoad

# simple statically determined shell 5.00 x 5.00 m with walls left, below, right

kx1 = KX.constRectangular(glo_dx=0.30, glo_dy=5.00)
ky1 = KY.constRectangular(glo_dx=0.30, glo_dy=5.00)

kx2 = KX.constRectangular(glo_dx=0.30, glo_dy=5.00)
ky2 = KY.constRectangular(glo_dx=0.30, glo_dy=5.00)

kx3 = KX.constRectangular(glo_dx=5.00, glo_dy=0.30)
ky3 = KY.constRectangular(glo_dx=5.00, glo_dy=0.30)

n1 = SupportNode(nr=1, glo_x=0.00, glo_y=2.50, glo_kx=kx1, glo_ky=ky1)
n2 = SupportNode(nr=2, glo_x=5.00, glo_y=2.50, glo_kx=kx2, glo_ky=ky2)
n3 = SupportNode(nr=3, glo_x=2.50, glo_y=0.00, glo_kx=kx3, glo_ky=ky3)

struc = Stucture(nodes=[n1, n2, n3], glo_mass_centre=(2.50, 2.50))

poly = Polygon(glob_xy=[[0, 0], [5, 0], [5, 5], [0, 5]])

# struc.to_rfem(poly, connect_to_server=False)

struc.printTable()

load = XYLoad(x_magnitude=1.00)

sol = LinSolve(structure=struc, load=load)
sol.printTable()

sol.to_mpl(poly, fscale=1, save=False, forces='torsion')