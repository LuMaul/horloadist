import numpy as np
import pandas as pd

from extract_node_stiffness import extractNodeStiffness


class SupportNode:
    def __init__(self, nr:int, glob_x:float, glob_y:float, glob_EIy:float, glob_EIx:float):
        self._nr = nr
        self._glob_x = glob_x
        self._glob_y = glob_y
        self._glob_EIy = glob_EIy
        self._glob_EIx = glob_EIx

        self._Rx = None
        self._Ry = None


class Polygon:
    def __init__(self, glob_xy:list[float,float]):
        self._xy = glob_xy

    @property
    def _xy_closed_polygon(self) -> np.ndarray:
        return np.vstack((self._xy, self._xy[0]))
    
    @property
    def _triangle_areas(self) -> np.ndarray:
        xy = self._xy_closed_polygon
        return np.cross(xy[:-1], xy[1:]) / 2
    
    @property
    def area(self) -> np.float64:
        return np.sum(self._triangle_areas)
    
    @property
    def _triangle_centroids(self) -> np.ndarray:
        xy = self._xy_closed_polygon
        return (xy[:-1] + xy[1:]) / 3

    @property
    def centroid(self) -> np.ndarray:
        tri_areas = self._triangle_areas
        tri_centr = self._triangle_centroids
        statical_moments = np.sum(tri_areas[:, np.newaxis] * tri_centr, axis=0)
        centroid = statical_moments / self.area
        return centroid
    

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



# fix +- error

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
            f"Fx, Fy      : {self._x_force}, {self._y_force}\n"
            f"tor. Ts,x : {self._torsion_Ts_from_x:0.4f}\n"
            f"tor. Ts,y : {self._torsion_Ts_from_y:0.4f}\n"
            f"tor. Ts     : {self._torsion_Ts :0.4f}\n"
            f"\n{self._table}\n"
            )
        

    def updateNodes(self) -> None:
        for node in self._structure._nodes:
            node._Rx = None




class NonLinSolve:
    def __init__(self, structure:Stucture, iterations:int=0):
        pass






if __name__ == '__main__':

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

    shear = LinSolve(struc, 0, 1)

    shear.printTable()


    # ky7 = extractNodeStiffness(7, Momentum=0)
    # ky8 = extractNodeStiffness(8, Momentum=0)
    # kx9 = extractNodeStiffness(9, Momentum=0)
    # ky10 = extractNodeStiffness(10, Momentum=0)
    # kx11 = extractNodeStiffness(11, Momentum=0)

    # w7 = SupportNode(7, 0.125, 1, 0, ky7)
    # w8 = SupportNode(8, 2.875, 1, 0, ky8)
    # w9 = SupportNode(9, 4, 2.125, kx9, 0)
    # w10 = SupportNode(10, 6.875, 3.5, 0, ky10)
    # w11 = SupportNode(11, 1.5, 4.875, kx11, 0)

    # xy = [[0, 0], [3, 0], [3, 2], [7, 2], [7, 5], [0, 5]]
    # poly = Polygon(xy)

    # nodes = [w7, w8, w9, w10, w11]
    # struc = Stucture(poly, nodes)

    # struc.printTable()

    # ls = LinSolve(struc, 200, 200)

    # ls.printTable()








