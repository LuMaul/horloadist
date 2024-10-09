from horloadist import SupportNode, Polygon, Stucture, LinSolve

def globalIy(dx, dy):
    return dy*dx**3/12

def globalIx(dx, dy):
    return dx*dy**3/12

w1 = SupportNode(1, -8, 3.0, globalIy(0.25, 4), globalIx(0.25, 4))
w2 = SupportNode(2, -2, 2.0, globalIy(0.25, 6), globalIx(0.25, 6))
w3 = SupportNode(3,  2,-5.0, globalIy(12,0.25), globalIx(12,0.25))
w4 = SupportNode(4,  0, 5.0, globalIy(4, 0.25), globalIx(4 ,0.25))

pl = Polygon([[8, 5], [8, -5], [-8, -5], [-8, 5]])

struc = Stucture(pl, [w1, w2, w3, w4])
struc.printTable()

sol = LinSolve(struc, 1, 1)
sol.printTable()