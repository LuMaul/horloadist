import pandas as pd
import numpy as np
from copy import deepcopy
import os

from .polygon import Polygon
from .stiffnesses import KX, KY
from .node import SupportNode
from .utils import interpolateXY
from .converters.to_rfem import init_rfem_model, to_rfem_node


class Stucture:
    """
    A class to represent a structural system defined by a polygon and a list of support nodes.

    Parameters
    ----------
    polygon : Polygon
        The polygon that defines the structural geometry.
    nodes : list of SupportNode
        A list of support nodes associated with the structure.
    
    Attributes
    ----------
    _polygon : Polygon
        The polygon object representing the structural geometry.
    _nodes : list of SupportNode
        List of support nodes forming the structure.
    _node_numbers : pd.Series
        Series representing the node numbers of the structure.
    _node_x : pd.Series
        Series representing the x-coordinates of the nodes.
    _node_y : pd.Series
        Series representing the y-coordinates of the nodes.
    _node_EIy : pd.Series
        Series representing the flexural stiffness of nodes along the y-axis.
    _node_EIx : pd.Series
        Series representing the flexural stiffness of nodes along the x-axis.
    _node_diff_x_xm : pd.Series
        Series representing the difference between node x-coordinates and the
        polygon centroid x-coordinate.
    _node_diff_y_ym : pd.Series
        Series representing the difference between node y-coordinates and the
        polygon centroid y-coordinate.
    _stiff_centre_x : float
        The x-coordinate of the stiffness center of the structure.
    _stiff_centre_y : float
        The y-coordinate of the stiffness center of the structure.
    _node_diff_xs_xm : pd.Series
        Series representing the difference between the stiffness center
        x-coordinate and node x-coordinates.
    _node_diff_ys_ym : pd.Series
        Series representing the difference between the stiffness center
        y-coordinate and node y-coordinates.
    _node_EIx_proportion : pd.Series
        Series representing the proportion of the total flexural stiffness
        along the x-axis for each node.
    _node_EIy_proportion : pd.Series
        Series representing the proportion of the total flexural stiffness
        along the y-axis for each node.
    _global_EIw : pd.Series
        Series representing the global warping stiffness.
    _node_EIwx_proportion : pd.Series
        Series representing the proportion of the torsional stiffness
        contribution for each node along the x-axis.
    _node_EIwy_proportion : pd.Series
        Series representing the proportion of the torsional stiffness
        contribution for each node along the y-axis.
    _result_table : pd.DataFrame
        DataFrame containing various structural properties and node data.
    """  
    def __init__(
            self,
            nodes:list[SupportNode],
            glo_mass_centre:tuple[float, float]|np.ndarray,
            verbose:bool=True
            ):
        
        self._nodes = nodes
        self._glo_mass_centre_x, self._glo_mass_centre_y = glo_mass_centre
        self._verbose = verbose
        self._linnodes = self._to_linear_nodes(deepcopy(nodes))


    def _to_linear_nodes(self, nodes:list[SupportNode]) -> list[SupportNode]:

        MOMENTUM = 0

        def printInfo(nr:int, axis:str, EI:float) -> None:
            if self._verbose:
                print(
                    f"Info: node {nr} -> took EI{axis}(Mom={MOMENTUM}) "
                    f"= {EI:,.1f} for linear solving"
                    )

        def extractStiffnessAtMomentZero(node:SupportNode) -> SupportNode:
            if isinstance(node._glob_EIx, pd.DataFrame):
                node._glob_EIx = interpolateXY(node._glob_EIx, MOMENTUM)
                printInfo(node._nr, 'x', node._glob_EIx)
            if isinstance(node._glob_EIy, pd.DataFrame):
                node._glob_EIy = interpolateXY(node._glob_EIy, MOMENTUM)
                printInfo(node._nr, 'y', node._glob_EIy)
            return node
        
        return [extractStiffnessAtMomentZero(node) for node in nodes]
    

    @property
    def _node_numbers(self) -> pd.Series:
        return pd.Series([node._nr for node in self._linnodes])
    
    @property
    def _glo_node_x(self) -> pd.Series:
        return pd.Series([node._glob_x for node in self._linnodes])

    @property
    def _glo_node_y(self) -> pd.Series:
        return pd.Series([node._glob_y for node in self._linnodes])
    
    @property
    def _loc_node_x(self) -> pd.Series:
        return self._glo_node_x - self._glo_mass_centre_x
    
    @property
    def _loc_node_y(self) -> pd.Series:
        return self._glo_node_y - self._glo_mass_centre_y

    @property
    def _node_EIy(self) -> pd.Series:
        return pd.Series([node._glob_EIy for node in self._linnodes])
    
    @property
    def _node_EIx(self) -> pd.Series:
        return pd.Series([node._glob_EIx for node in self._linnodes])
    
    @property
    def _loc_stiff_centre_x(self) -> float:
        x_xm = self._loc_node_x
        EIx = self._node_EIx
        return (EIx * x_xm).sum() / EIx.sum()

    @property
    def _loc_stiff_centre_y(self) -> float:
        y_ym = self._loc_node_y
        EIy = self._node_EIy
        return (EIy * y_ym).sum() / EIy.sum()

    @property
    def _glo_stiff_centre_x(self) -> float:
        return self._loc_stiff_centre_x + self._glo_mass_centre_x

    @property
    def _glo_stiff_centre_y(self) -> float:
        return self._loc_stiff_centre_y + self._glo_mass_centre_y

    @property
    def _loc_node_xs(self) -> pd.Series:
        return self._glo_node_x - self._glo_stiff_centre_x
    
    @property
    def _loc_node_ys(self) -> pd.Series:
        return self._glo_node_y - self._glo_stiff_centre_y
    
    @property
    def _node_EIx_proportion(self) -> pd.Series:
        return self._node_EIy / self._node_EIy.sum()
    
    @property
    def _node_EIy_proportion(self) -> pd.Series:
        return self._node_EIx / self._node_EIx.sum()
    
    @property
    def _global_EIw(self) -> pd.Series:
        EIy = self._node_EIy
        EIx = self._node_EIx
        x = self._loc_node_xs
        y = self._loc_node_ys
        return (EIy*y**2 + EIx*x**2).sum()
    
    @property
    def _node_EIwx_proportion(self) -> pd.Series:
        return self._node_EIy * self._loc_node_ys / self._global_EIw
    
    @property
    def _node_EIwy_proportion(self) -> pd.Series:
        return self._node_EIx * self._loc_node_xs / self._global_EIw
    
    @property
    def _result_table(self) -> pd.DataFrame:

        result_table = {
            'node nr':self._node_numbers,
            'glo x':self._glo_node_x,
            'glo y':self._glo_node_y,
            'loc x':self._loc_node_x,
            'loc y':self._loc_node_y,
            'loc xs ':self._loc_node_xs,
            'loc ys':self._loc_node_ys,
            'EIx':self._node_EIx,
            'EIy':self._node_EIy,
            '% EIx':self._node_EIx_proportion,
            '% EIy':self._node_EIy_proportion,
            '% EIwx':self._node_EIwx_proportion,
            '% EIwy':self._node_EIwy_proportion
        }

        return pd.DataFrame(result_table)


    def printTable(self) -> None:
        """
        Prints a detailed summary of the structure's geometric and stiffness properties.

        This method outputs the polygon area, centroid, stiffness center, total stiffness 
        in x and y directions, as well as the global warping stiffness. It also prints 
        a table with node-specific data such as coordinates, stiffness proportions, 
        and torsional stiffness contributions.

        Returns
        -------
        None
        """
        print(
            "\n"
            f"glo mass   centre [x,y] : "
            f"{self._glo_mass_centre_x:0.4f}, "
            f"{self._glo_mass_centre_y:0.4f}\n"
            f"glo stiff. centre [x,y] : "
            f"{self._glo_stiff_centre_x:0.4f}, "
            f"{self._glo_stiff_centre_y:0.4f}\n"
            f"loc stiff. centre [x,y] : "
            f"{self._loc_stiff_centre_x:0.4f}, "
            f"{self._loc_stiff_centre_y:0.4f}\n"
            f"EIx total               : "
            f"{self._node_EIx.sum():,.1f}\n"
            f"EIy total               : "
            f"{self._node_EIy.sum():,.1f}\n"
            f"EIw total               : "
            f"{self._global_EIw:,.1f}\n"
            f"\n{self._result_table}\n"
            )
        

    def to_rfem(self, model_name:str=f'{os.path.basename(__file__)}.rf6', *model_args) -> None:
        init_rfem_model(model_name, *model_args)
        to_rfem_node(node=None)