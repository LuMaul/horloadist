import pandas as pd

from .stiffnesses import KX, KY


class XYSupportNode:
    """
    A class to represent a support node in a structural system.

    Parameters
    ----------
    nr : int
        Node number (identifier).
    glob_x : float
        Global x-coordinate of the node.
    glob_y : float
        Global y-coordinate of the node.
    glob_EIy : float
        Global stiffness value along the y-axis (bending stiffness).
    glob_EIx : float
        Global stiffness value along the x-axis (bending stiffness).

    Attributes
    ----------
    _nr : int
        Node number (identifier).
    _glob_x : float
        Global x-coordinate of the node.
    _glob_y : float
        Global y-coordinate of the node.
    _glob_EIy : float
        Stiffness along the y-axis.
    _glob_EIx : float
        Stiffness along the x-axis.
    _Rx : float, optional
        Reaction force along the x-axis at the node, initialized to None.
    _Ry : float, optional
        Reaction force along the y-axis at the node, initialized to None.
    """
    def __init__(
            self,
            nr:int,
            glo_x:float,
            glo_y:float,
            glo_kx:float|pd.DataFrame,
            glo_ky:float|pd.DataFrame
            ):
        self._nr = nr
        self._glo_x = glo_x
        self._glo_y = glo_y
        self._glo_EIy = glo_kx
        self._glo_EIx = glo_ky

        # updated via Solvers
        self._Rx = 0.0
        self._Ry = 0.0


class ZSupportNode:
    def __init__(
            self,
            nr:int,
            glo_x:float,
            glo_y:float,
            ):
        
        self._nr = nr
        self._glo_x = glo_x
        self._glo_y = glo_y