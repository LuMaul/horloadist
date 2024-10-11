from horloadist import KX, KY, SupportNode, Polygon, Stucture, LinSolve, NonLinSolve
from horloadist.utils import plot_nlsolve

import os
import pandas as pd


def constrPth(fname:str) -> str:
    CSV_ROOT = 'stiffness_data'
    return os.path.join(CSV_ROOT, fname)

kx7 = KX.from_csv(constrPth('7 mchi csa N-41.4 kN.csv'), 'mom', 'EI')
kx8 = KX.from_csv(constrPth('8 mchi csa N-30.3 kN.csv'), 'mom', 'EI')
ky9 = KY.from_csv(constrPth('9 mchi csa N-92.1 kN.csv'), 'mom', 'EI')
kx10 = KX.from_csv(constrPth('10 mchi csa N-49.9 kN.csv'), 'mom', 'EI')
ky11 = KY.from_csv(constrPth('10 mchi csa N-49.9 kN.csv'), 'mom', 'EI')


w7 = SupportNode(7, 0.125, 1, kx7, 0)
w8 = SupportNode(8, 2.875, 1, kx8, 0)
w9 = SupportNode(9, 4, 2.125, 0, ky9)
w10 = SupportNode(10, 6.875, 3.5, kx10, 0)
w11 = SupportNode(11, 1.5, 4.875, 0, ky11)

shell = Polygon(glob_xy=[[0, 0], [3, 0], [3, 2], [7, 2], [7, 5], [0, 5]])

struc = Stucture(shell, [w7, w8, w9, w10, w11], verbose=False)

sol = NonLinSolve(struc, 1000, 1000, z_heigt=5)

# sol.printIterationTable()

res = sol._table_onlyUpdates

plot_nlsolve(res, show=True, save=False)



