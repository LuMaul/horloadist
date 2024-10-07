from horloadist import SupportNode, Polygon, Stucture, LinSolve

# Caution! Do not blindly trust this calculation, but always check
# the plausibility of the results.

def globalIy(dx, dy):
    if dx > dy:
        return 0
    return dx*dy**3/12

def globalIx(dx, dy):
    if dy > dx:
        return 0
    return dy*dx**3/12


w1 = SupportNode(1, -10.0, -2.5, globalIx(5, 0.3), globalIy(5, 0.3))
w2 = SupportNode(2, -12.5,  0.0, globalIx(0.3, 5), globalIy(0.3, 5))
w3 = SupportNode(3, -10.0,  2.5, globalIx(5, 0.3), globalIy(5, 0.3))
w4 = SupportNode(4,   0.0, -7.5, globalIx(5, 0.3), globalIy(5, 0.3))
w5 = SupportNode(5,   2.5,  7.5, globalIx(10,0.3), globalIy(10,0.3))
w6 = SupportNode(6,   7.5,  0.0, globalIx(0.3, 5), globalIy(0.3, 5))
w7 = SupportNode(7,  12.5, -5.0, globalIx(0.3, 5), globalIy(0.3, 5))


plate = Polygon([[-12.5, -7.5], [-12.5, 7.5], [12.5, 7.5], [12.5, -7.5]])


struc = Stucture(plate, [w1, w2, w3, w4, w5, w6, w7])
struc.printTable()


sol = LinSolve(struc, 0, 1)
sol.printTable()