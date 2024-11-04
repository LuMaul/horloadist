from horloadist import KX, KY, Polygon, SupportNode, Stucture, LinSolve

# simple statically determined shell 5.00 x 5.00 m with walls left, below, right

kx1 = KX.constRectangular(dx_glob=0.30, dy_glob=5.00)
ky1 = KY.constRectangular(dx_glob=0.30, dy_glob=5.00)

kx2 = KX.constRectangular(dx_glob=0.30, dy_glob=5.00)
ky2 = KY.constRectangular(dx_glob=0.30, dy_glob=5.00)

kx3 = KX.constRectangular(dx_glob=5.00, dy_glob=0.30)
ky3 = KY.constRectangular(dx_glob=5.00, dy_glob=0.30)

n1 = SupportNode(nr=1, glob_x=0.00, glob_y=2.50, glob_kx=kx1, glob_ky=ky1)
n2 = SupportNode(nr=2, glob_x=5.00, glob_y=2.50, glob_kx=kx2, glob_ky=ky2)
n3 = SupportNode(nr=3, glob_x=2.50, glob_y=0.00, glob_kx=kx3, glob_ky=ky3)

struc = Stucture(nodes=[n1, n2, n3], glo_mass_centre=(2.50, 2.50))

struc.to_rfem()

struc.printTable()

sol = LinSolve(structure=struc, x_mass_force=1.00, y_mass_force=0.00)
sol.printTable()