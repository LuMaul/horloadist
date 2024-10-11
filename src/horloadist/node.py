import pandas as pd

from .stiffnesses import KX, KY


class SupportNode:
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
            glob_x:float,
            glob_y:float,
            glob_kx:float|pd.DataFrame,
            glob_ky:float|pd.DataFrame
            ):
        self._nr = nr
        self._glob_x = glob_x
        self._glob_y = glob_y
        self._glob_EIy = glob_kx
        self._glob_EIx = glob_ky

        # updated via Solvers
        self._Rx = 0.0
        self._Ry = 0.0


