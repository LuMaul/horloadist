import pandas as pd
import numpy as np
import scipy.integrate as sc_int

from horloadist.node import XYSupportNode
from horloadist.linsolve import LinSolve


class ZBeamElement:
    """
    A class representing a pseudo Z-beam element for structural analysis.

    This class handles the calculation of shear forces, moments, and other structural
    properties along the Z-axis of a beam element.

    Parameters
    ----------
    node : XYSupportNode
        Node object containing position and identification information.
    z_num_floors : int
        Number of floors (divisions) along the Z-axis.
    z_floor_heigt : float
        Height of each floor (division length) along the Z-axis.
    const_f_x : float
        Constant force in the X direction.
    const_f_y : float
        Constant force in the Y direction.
    const_f_z : float, optional
        Constant force in the Z direction, by default 0.00.

    Attributes
    ----------
    _no : int
        Element identification number from node.
    _glo_x : float
        Global X-coordinate from node.
    _glo_y : float
        Global Y-coordinate from node.
    _z_num_floors : int
        Number of floors.
    _z_floor_heigt : float
        Height of each floor.
    _const_f_x : float
        Constant X force.
    _const_f_y : float
        Constant Y force.
    _const_f_z : float
        Constant Z force.
    """
    def __init__(
            self,
            node:XYSupportNode,
            z_num_floors:int,
            z_floor_heigt:float,
            const_f_x:float,
            const_f_y:float,
            const_f_z:float=0.00,
            ) -> None:
        
        self._no = node._nr
        self._glo_x = node._glo_x
        self._glo_y = node._glo_y

        self._z_num_floors = z_num_floors
        self._z_floor_heigt = z_floor_heigt

        self._const_f_x = const_f_x
        self._const_f_y = const_f_y
        self._const_f_z = const_f_z


    @property
    def _z_heigt(self) -> float:
        return self._z_num_floors * self._z_floor_heigt

    @property
    def _glo_z_cords(self) -> pd.Series:
        z_cords = []
        for z_index in range(int(self._z_num_floors)):
            z_sta = z_index * self._z_floor_heigt
            z_end = (z_index + 1) * self._z_floor_heigt
            z_cords.append(z_sta)
            z_cords.append(z_end)

        return pd.Series(np.flip(z_cords))

    @property
    def _glo_x_cords(self) -> pd.Series:
        return pd.Series(np.full_like(self._glo_z_cords, self._glo_x))

    @property
    def _glo_y_cords(self) -> pd.Series:
        return pd.Series(np.full_like(self._glo_z_cords, self._glo_y))


    def _integrate_over_z(self, f_arr:pd.Series) -> pd.Series:
        integral = sc_int.cumulative_trapezoid(f_arr, self._glo_z_cords, initial=0)
        return pd.Series(integral)


    def _shear_cumsum(self, f_const:float) -> pd.Series: # could be more elegant
        f_arr = np.cumsum(np.full_like(self._glo_z_cords[::2], f_const)).repeat(2)
        return pd.Series(f_arr)


    @property
    def _glo_x_shear(self) -> pd.Series:
        return self._shear_cumsum(self._const_f_x)

    @property
    def _glo_y_shear(self) -> pd.Series:
        return self._shear_cumsum(self._const_f_y)

    @property
    def _glo_z_normf(self) -> pd.Series:
        return self._shear_cumsum(self._const_f_z)

    @staticmethod
    def _flip(series:pd.Series) -> pd.Series:
        return series.iloc[::-1].reset_index(drop=True)




    @property
    def _glo_y_moments(self) -> pd.Series:
        return pd.Series(self._integrate_over_z(self._glo_x_shear))

    @property
    def _glo_x_moments(self) -> pd.Series:
        return pd.Series(self._integrate_over_z(self._glo_y_shear))


    @property
    def _result_table(self) -> pd.DataFrame:

        results = {
            'glo_x':self._glo_x_cords,
            'glo_y':self._glo_y_cords,
            'glo_z':self._glo_z_cords,
            'glo_Vx':self._glo_x_shear,
            'glo_Vy':self._glo_y_shear,
            'glo_My':self._glo_y_moments,
            'glo_Mx':self._glo_x_moments,
            'glo_N':self._glo_z_normf,
        }

        return pd.DataFrame(results)


    def printTable(self) -> pd.DataFrame:
        """
        Print a summary of the element's properties and return results table.

        Prints element information including:
        - Node number
        - Global coordinates
        - Z-axis properties
        - Constant forces
        - Results table with coordinates, shear forces, and moments

        Returns
        -------
        pd.DataFrame
            DataFrame containing the element's structural analysis results including:
            - Global coordinates (x, y, z)
            - Shear forces (Vx, Vy)
            - Moments (Mx, My)
        """
        
        res_msg = (
            f"node nr   : {self._no} \n"
            f"glo [x,y] : {self._glo_x:0.4f}, {self._glo_y:0.4f}\n"
            f"z number  : {self._z_num_floors} \n"
            f"z div     : {self._z_floor_heigt} \n"
            f"heigt     : {self._z_heigt} \n"
            "-----------------------------------\n"
            f"const glo fx  : {self._const_f_x} \n"
            f"const glo fy  : {self._const_f_y} \n"
            f"const glo fz  : {self._const_f_z} \n"
            "-----------------------------------\n"
            f"{self._result_table}"
        )

        print(res_msg)

        return self._result_table