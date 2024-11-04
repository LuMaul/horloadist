from horloadist import KX, KY, SupportNode, Polygon, Stucture, NonLinSolve, XYLoad
from horloadist.utils import plot_nlsolve

import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def constrPth(fname:str) -> str:
    CSV_ROOT = 'stiffness_data'
    return os.path.join(CSV_ROOT, fname)

ky7 = KX.from_csv(constrPth('7 mchi csa N-41.4 kN.csv'), 'mom', 'EI')
ky8 = KX.from_csv(constrPth('8 mchi csa N-30.3 kN.csv'), 'mom', 'EI')
kx9 = KY.from_csv(constrPth('9 mchi csa N-92.1 kN.csv'), 'mom', 'EI')
ky10 = KX.from_csv(constrPth('10 mchi csa N-49.9 kN.csv'), 'mom', 'EI')
kx11 = KY.from_csv(constrPth('10 mchi csa N-49.9 kN.csv'), 'mom', 'EI')


w7 = SupportNode(7, 0.125, 1, 0, ky7)
w8 = SupportNode(8, 2.875, 1, 0, ky8)
w9 = SupportNode(9, 4, 2.125, kx9, 0)
w10 = SupportNode(10, 6.875, 3.5, 0, ky10)
w11 = SupportNode(11, 1.5, 4.875, kx11, 0)

shell = Polygon(glob_xy=[[0, 0], [3, 0], [3, 2], [7, 2], [7, 5], [0, 5]])

struc = Stucture(nodes=[w7, w8, w9, w10, w11], glo_mass_centre=shell.centroid, verbose=False)

load = XYLoad(x_magnitude=1000, y_magnitude=1000)

sol = NonLinSolve(struc, load, z_heigt=5)

# sol.printIterationTable()

res = sol._table_onlyUpdates

plot_nlsolve(res, show=True, save=False, fname='example_nlsolve', format='png')



