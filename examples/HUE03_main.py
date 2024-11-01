from horloadist import SupportNode, Polygon, Stucture, LinSolve



def globalIy(dx, dy):
    return dy*dx**3/12

def globalIx(dx, dy):
    return dx*dy**3/12


w1 = SupportNode(nr=1, glob_x=-10.0,  glob_y=2.5, glob_kx=globalIy(5, 0.3), glob_ky=globalIx(5, 0.3))
w2 = SupportNode(nr=2, glob_x=-12.5,  glob_y=0.0, glob_kx=globalIy(0.3, 5), glob_ky=globalIx(0.3, 5))
w3 = SupportNode(nr=3, glob_x=-10.0,  glob_y=-2.5, glob_kx=globalIy(5, 0.3), glob_ky=globalIx(5, 0.3))
w4 = SupportNode(nr=4, glob_x=    0,  glob_y=7.5, glob_kx=globalIy(5, 0.3), glob_ky=globalIx(5, 0.3))
w5 = SupportNode(nr=5, glob_x=  2.5,  glob_y=-7.5, glob_kx=globalIy(10,0.3), glob_ky=globalIx(10,0.3))
w6 = SupportNode(nr=6, glob_x=  7.5,  glob_y=0.0, glob_kx=globalIy(0.3, 5), glob_ky=globalIx(0.3, 5))
w7 = SupportNode(nr=7, glob_x= 12.5,  glob_y=5.0, glob_kx=globalIy(0.3, 5), glob_ky=globalIx(0.3, 5))

plate = Polygon(glob_xy=[[-12.5,-7.5], [12.5, -7.5], [12.5, 7.5], [-12.5, 7.5]])


struc = Stucture(nodes=[w1, w2, w3, w4, w5, w6, w7], glo_mass_centre=plate.centroid)
struc.printTable()


sol = LinSolve(structure=struc, x_mass_force=0, y_mass_force=-1)
sol.printTable()