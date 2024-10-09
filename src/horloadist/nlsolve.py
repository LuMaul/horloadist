import pandas as pd

from .node import SupportNode
from .structure import Stucture
from .utils import interpolateXY
from .linsolve import LinSolve

class NonLinSolve:
    def __init__(
            self,
            structure:Stucture,
            x_mass_force:float=1,
            y_mass_force:float=1,
            iterations:int=10
            ) -> None:
        
        self._structure = structure
        self._x_force = x_mass_force
        self._y_force = y_mass_force
        self._iterations = iterations
        
        self._nodes = self._structure._allnodes

        self._solve()


    def _solve(self) -> None:

        new_structure = Stucture(
            self._structure._polygon,
            self._nodes,
            verbose=False
        )

        sol = LinSolve(new_structure, self._x_force, self._y_force)
        sol.printTable()
        sol.updateNodes()

        # continue developing with updating stiffnesses
        print(new_structure._allnodes[0]._Ry)