import pandas as pd

from .polygon import Polygon
from .node import SupportNode

class Stucture:
    def __init__(self, polygon:Polygon, nodes:list[SupportNode]):
        
        self._polygon = polygon
        self._nodes = nodes

    
    @property
    def _node_numbers(self) -> pd.Series:
        return pd.Series([node._nr for node in self._nodes])
    
    @property
    def _node_x(self) -> pd.Series:
        return pd.Series([node._glob_x for node in self._nodes])

    @property
    def _node_y(self) -> pd.Series:
        return pd.Series([node._glob_y for node in self._nodes])
    
    @property
    def _node_EIy(self) -> pd.Series:
        return pd.Series([node._glob_EIy for node in self._nodes])
    
    @property
    def _node_EIx(self) -> pd.Series:
        return pd.Series([node._glob_EIx for node in self._nodes])
    
    @property
    def _node_diff_x_xm(self) -> pd.Series:
        return self._node_x - self._polygon.centroid[0]
    
    @property
    def _node_diff_y_ym(self) -> pd.Series:
        return self._node_y - self._polygon.centroid[1]

    @property
    def _stiff_centre_x(self) -> float:
        x_xm = self._node_diff_x_xm
        EIx = self._node_EIx
        return (EIx * x_xm).sum() / EIx.sum()

    @property
    def _stiff_centre_y(self) -> float:
        y_ym = self._node_diff_y_ym
        EIy = self._node_EIy
        return (EIy * y_ym).sum() / EIy.sum()
    
    @property
    def _node_diff_xs_xm(self) -> pd.Series:
        return self._stiff_centre_x - self._node_x
    
    @property
    def _node_diff_ys_ym(self) -> pd.Series:
        return self._stiff_centre_y - self._node_y
    
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
        x = self._node_diff_xs_xm
        y = self._node_diff_ys_ym
        return (EIy*y**2 + EIx*x**2).sum()
    
    @property
    def _node_EIwx_proportion(self) -> pd.Series:
        return self._node_EIy * self._node_diff_ys_ym / self._global_EIw
    
    @property
    def _node_EIwy_proportion(self) -> pd.Series:
        return self._node_EIx * self._node_diff_xs_xm / self._global_EIw
    
    @property
    def _result_table(self) -> pd.DataFrame:

        result_table = {
            'node nr':self._node_numbers,
            'x':self._node_x,
            'y':self._node_y,
            'x-xm':self._node_diff_x_xm,
            'y-ym':self._node_diff_y_ym,
            'xm-xs ':self._node_diff_xs_xm,
            'ym-ys':self._node_diff_ys_ym,
            'EIy':self._node_EIy,
            'EIx':self._node_EIx,
            '% EIx':self._node_EIx_proportion,
            '% EIy':self._node_EIy_proportion,
            '% EIwx':self._node_EIwx_proportion,
            '% EIwy':self._node_EIwy_proportion
        }

        return pd.DataFrame(result_table)


    def printTable(self) -> None:
        print(
            "\n"
            f"polyg. area           : "
            f"{self._polygon.area:0.4f}\n"
            f"polyg. centre [xm,ym] : "
            f"{self._polygon.centroid[0]:0.4f}, "
            f"{self._polygon.centroid[1]:0.4f} \n"
            f"stiff. centre [xs,ys] : "
            f"{self._stiff_centre_x:0.4f}, "
            f"{self._stiff_centre_y:0.4f}\n"
            f"EIx total             : "
            f"{self._node_EIx.sum():,.1f}\n"
            f"EIy total             : "
            f"{self._node_EIy.sum():,.1f}\n"
            f"EIw total             : "
            f"{self._global_EIw:,.1f}\n"
            f"\n{self._result_table}\n"
            )