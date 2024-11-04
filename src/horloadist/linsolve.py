import pandas as pd

from horloadist.node import SupportNode
from horloadist.polygon import Polygon
from horloadist.structure import Stucture
from horloadist.loads import XYLoad

import horloadist.converters.to_rfem as rfem_conv


class LinSolve:
    """
    A class to represent the linear solver for a structure subjected to forces and torsion.
    
    This solver calculates forces and moments on a structure based on applied loads,
    eccentricities, and nodal properties. It can also convert these forces to a format
    compatible with RFEM models.

    Parameters
    ----------
    structure : Structure
        The structure object containing geometry and stiffness details.
    load : XYLoad
        Load object specifying magnitudes of x and y forces applied to the structure.

    Attributes
    ----------
    _structure : Structure
        The structure object with geometry and stiffness properties.
    _x_force : float
        The force applied along the x-axis.
    _y_force : float
        The force applied along the y-axis.
    _torsion_Ts_from_x : float
        Torsion moment caused by the x-direction force.
    _torsion_Ts_from_y : float
        Torsion moment caused by the y-direction force.
    _torsion_Ts : float
        Total torsion moment due to forces in both x and y directions.
    _node_Vx_from_EIx : pd.Series
        Nodal forces in the x-direction based on flexural rigidity (EIx).
    _node_Vy_from_EIy : pd.Series
        Nodal forces in the y-direction based on flexural rigidity (EIy).
    _node_Ts_from_EIwx : pd.Series
        Nodal forces in the x-direction due to torsion moments (EIwx).
    _node_Ts_from_EIwy : pd.Series
        Nodal forces in the y-direction due to torsion moments (EIwy).
    _node_final_Vx : pd.Series
        Final x-directional nodal force, accounting for both flexural and torsional effects.
    _node_final_Vy : pd.Series
        Final y-directional nodal force, accounting for both flexural and torsional effects.
    _table : pd.DataFrame
        DataFrame containing all calculated nodal forces, including torsional effects.
    """ 
    def __init__(self, structure:Stucture, load:XYLoad):
        self._structure = structure
        self._load = load
        self._x_force = self._load._x_magnitude
        self._y_force = self._load._y_magnitude

    @property
    def _eccentricity_x(self):
        return self._structure._loc_stiff_centre_x
    
    @property
    def _eccentricity_y(self):
        return self._structure._loc_stiff_centre_y

    @property
    def _torsion_Ts_from_x(self) -> float:
        return  self._x_force * (self._eccentricity_y)
    
    @property
    def _torsion_Ts_from_y(self) -> float:
        return -self._y_force * (self._eccentricity_x)
    
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
    def _node_Ts_from_EIwx(self) -> pd.Series:
        return - self._structure._node_EIwx_proportion * self._torsion_Ts
    
    @property
    def _node_Ts_from_EIwy(self) -> pd.Series:
        return   self._structure._node_EIwy_proportion * self._torsion_Ts
    
    @property
    def _node_final_Vx(self) -> pd.Series:
        return self._node_Vx_from_EIx + self._node_Ts_from_EIwx
    
    @property
    def _node_final_Vy(self) -> pd.Series:
        return self._node_Vy_from_EIy + self._node_Ts_from_EIwy
    

    @property
    def _table(self) -> pd.DataFrame:
        
        result_table = {
            'node nr':self._structure._node_numbers,
            'Vx ~ EIx':self._node_Vx_from_EIx,
            'Vy ~ EIy':self._node_Vy_from_EIy,
            'Ts ~ -EIwx':self._node_Ts_from_EIwx,
            'Ts ~ EIwy':self._node_Ts_from_EIwy,
            'Vx':self._node_final_Vx,
            'Vy':self._node_final_Vy,
        }

        return pd.DataFrame(result_table)
        

    def printTable(self) -> None:
        """
        Prints the forces acting on the structure, including the mass forces, torsion forces, 
        and a table of nodal forces.

        This method outputs the x and y forces, torsion moments, and the detailed 
        DataFrame containing nodal forces in the x and y directions.
        
        Returns
        -------
        None
        """
        print(
            "\n"
            f"Fx, Fy                  : {self._x_force}, {self._y_force}\n"
            f"ex, ey                  : {self._eccentricity_x:0.4f}, {self._eccentricity_y:0.4f}\n"
            f"tor. Ts,x  =  Fx * ey   : {self._torsion_Ts_from_x:0.4f}\n"
            f"tor. Ts,y  =  Fy * ex   : {self._torsion_Ts_from_y:0.4f}\n"
            f"tor. Ts = Ts,x + Ts,y   : {self._torsion_Ts :0.4f}\n"
            f"\n{self._table}\n"
            )
        

    def updateNodes(self) -> None:
        """
        Updates the reaction forces (Rx, Ry) for each node in the structure.

        This method calculates the x and y reaction forces for each node based on the 
        computed nodal forces and assigns them to the node's attributes.

        Returns
        -------
        None
        """
        def extracVxByNode(node:SupportNode) -> float:
            rx = self._table['Vx'].loc[self._table['node nr'] == node._nr]
            return float(rx.iloc[0])
        
        def extracVyByNode(node:SupportNode) -> float:
            ry = self._table['Vy'].loc[self._table['node nr'] == node._nr]
            return float(ry.iloc[0])

        for node in self._structure._linnodes:
            node._Rx = -extracVxByNode(node)
            node._Ry = -extracVyByNode(node)


    def to_rfem(self, polygon:Polygon, **rfem_model_kwargs) -> None:
        rfem_conv.init_rfem_model(**rfem_model_kwargs)

        # rfem_conv.Model.clientModel.service.begin_modification()

        for node in self._structure._nodes:
            rfem_conv.to_rfem_support_node(node=node)

        shell_info = rfem_conv.to_rfem_shell(polygon)
        shell_tag = list(shell_info)[0]

        glo_x, glo_y = polygon.centroid
        rfem_conv.to_rfem_free_load(glo_x, glo_y, shell_tag, self._load)

        # rfem_conv.Model.clientModel.service.finish_modification()

        # rfem_conv.Calculate_all()
