import pandas as pd

from .node import SupportNode
from .structure import Stucture

class LinSolve:
    def __init__(self, structure:Stucture, x_mass_force:float=1, y_mass_force:float=1):
        
        self._structure = structure
        self._x_force = x_mass_force
        self._y_force = y_mass_force

    @property
    def _torsion_Ts_from_x(self) -> float:
        return -self._x_force * (self._structure._polygon.centroid[1]-self._structure._stiff_centre_y)
    
    @property
    def _torsion_Ts_from_y(self) -> float:
        return  self._y_force * (self._structure._polygon.centroid[0]-self._structure._stiff_centre_x)
    @property
    def _torsion_Ts(self) -> float:
        return self._torsion_Ts_from_x + self._torsion_Ts_from_y

    @property
    def _node_Vx_from_EIx(self) -> pd.Series:
        return self._structure._node_EIx_proportion * self._x_force
    
    @property
    def _node_Vy_from_EIy(self) -> pd.Series:
        return self._structure._node_EIy_proportion * self._y_force
    
    @property
    def _node_Vx_from_EIwx(self) -> pd.Series:
        return self._structure._node_EIwx_proportion * self._torsion_Ts
    
    @property
    def _node_Vy_from_EIwy(self) -> pd.Series:
        return self._structure._node_EIwy_proportion * self._torsion_Ts
    
    @property
    def _node_final_Vx(self) -> pd.Series:
        return self._node_Vx_from_EIx - self._node_Vx_from_EIwx
    
    @property
    def _node_final_Vy(self) -> pd.Series:
        return self._node_Vy_from_EIy + self._node_Vy_from_EIwy
    

    @property
    def _table(self) -> pd.DataFrame:
        
        result_table = {
            'node nr':self._structure._node_numbers,
            'Vx ~ EIx':self._node_Vx_from_EIx,
            'Vy ~ EIy':self._node_Vy_from_EIy,
            'Vx ~ EIwx':self._node_Vx_from_EIwx,
            'Vy ~ EIwy':self._node_Vy_from_EIwy,
            'Vx':self._node_final_Vx,
            'Vy':self._node_final_Vy,
        }

        return pd.DataFrame(result_table)
        

    def printTable(self) -> None:
        print(
            "\n"
            f"Fx, Fy    : {self._x_force}, {self._y_force}\n"
            f"tor. Ts,x : {self._torsion_Ts_from_x:0.4f}\n"
            f"tor. Ts,y : {self._torsion_Ts_from_y:0.4f}\n"
            f"tor. Ts   : {self._torsion_Ts :0.4f}\n"
            f"\n{self._table}\n"
            )
        

    def updateNodes(self) -> None:

        def extracVxByNode(node:SupportNode) -> float:
            rx = self._table['Vx'].loc[self._table['node nr'] == node._nr]
            return float(rx.iloc[0])
        
        def extracVyByNode(node:SupportNode) -> float:
            ry = self._table['Vy'].loc[self._table['node nr'] == node._nr]
            return float(ry.iloc[0])

        for node in self._structure._nodes:
            node._Rx = -extracVxByNode(node)
            node._Ry = -extracVyByNode(node)