import pandas as pd
import numpy as np

from .node import SupportNode
from .structure import Stucture
from .utils import interpolateXY
from .linsolve import LinSolve

class NonLinSolve:
    """
    A class for non-linear solving of structural problems.

    This class implements a non-linear solver for structural analysis, 
    considering the effects of geometric non-linearity.

    Parameters
    ----------
    structure : Stucture
        The structural model to be analyzed.
    x_mass_force : float, optional
        The mass force in the x-direction (default is 1).
    y_mass_force : float, optional
        The mass force in the y-direction (default is 1).
    iterations : int, optional
        The number of iterations for the non-linear solution (default is 40).
    z_heigt : float, optional
        The height in the z-direction for moment calculations (default is 1).
    verbose : bool, optional
        If True, print iteration progress (default is True).

    Attributes
    ----------
    _structure : Stucture
        The structural model being analyzed.
    _x_force : float
        The mass force in the x-direction.
    _y_force : float
        The mass force in the y-direction.
    _iterations : int
        The number of iterations for the non-linear solution.
    _z_heigt : float
        The height in the z-direction for moment calculations.
    _verbose : bool
        Flag for verbose output.
    _node_tracker : dict
        Dictionary to track node properties across iterations.
    _structure_tracker : dict
        Dictionary to track structure properties across iterations.
    _table : pd.DataFrame
        DataFrame containing all tracked data across iterations.
    _table_onlyUpdates : pd.DataFrame
        DataFrame containing only the data that changed across iterations.
    """      
    def __init__(
            self,
            structure:Stucture,
            x_mass_force:float=1,
            y_mass_force:float=1,
            iterations:int=40,
            z_heigt:float=1,
            verbose:bool=True
            ) -> None:
        self._structure = structure
        self._x_force = x_mass_force
        self._y_force = y_mass_force
        self._iterations = iterations
        self._z_heigt = z_heigt

        self._verbose = verbose
        
        self._main()


    def _init_node_tracker(self) -> None:
        self._node_tracker = {}
        for node in self._structure._linnodes:
            self._update_node_tracker(node, init=True)


    def _append_node_tracker(self) -> None:
        for node in self._structure._linnodes:
            self._update_node_tracker(node)


    def _update_node_tracker(self, node:SupportNode, init=False) -> None:
        TRACKING_REGISTER = {
            f'node {node._nr} EIx':[node._glob_EIx],
            f'node {node._nr} EIy':[node._glob_EIy],
            f'node {node._nr} Vx':[-node._Rx],
            f'node {node._nr} Vy':[-node._Ry],
            f'node {node._nr} Mx':[-node._Ry * self._z_heigt],
            f'node {node._nr} My':[-node._Rx * self._z_heigt]
        }
        if init:
            for key, item in TRACKING_REGISTER.items():
                self._node_tracker[key] = item
        else:
            for key, item in TRACKING_REGISTER.items():
                self._node_tracker[key].append(item[0])



    def _init_structure_tracker(self) -> None:
        self._structure_tracker = {}
        self._update_structure_tracker(self._structure, init=True)


    def _append_structure_tracker(self) -> None:
        self._update_structure_tracker(self._structure)


    def _update_structure_tracker(self, structure:Stucture, init=False) -> None:
        TRACKING_REGISTER = {
            f'x_s':[structure._stiff_centre_x],
            f'y_s':[structure._stiff_centre_y],
        }
        if init:
            for key, item in TRACKING_REGISTER.items():
                self._structure_tracker[key] = item
        else:
            for key, item in TRACKING_REGISTER.items():
                self._structure_tracker[key].append(item[0])


    
        
    def _update_linnodes_inplace(self) -> None:
        nodes_and_linnodes = zip(
            self._structure._nodes,
            self._structure._linnodes
            )
        for node, linnode in nodes_and_linnodes:
            if isinstance(node._glob_EIx, pd.DataFrame):
                linnode._glob_EIx = interpolateXY(
                    node._glob_EIx,
                    -linnode._Ry*self._z_heigt
                    )
            if isinstance(node._glob_EIy, pd.DataFrame):
                linnode._glob_EIy = interpolateXY(
                    node._glob_EIy,
                    -linnode._Rx*self._z_heigt
                    )


    def _linsolve_inplace(self) -> None:
        sol = LinSolve(self._structure, self._x_force, self._y_force)
        sol.updateNodes()


    def _iterate(self) -> None:
        self._init_structure_tracker()
        self._init_node_tracker()
        for i, _ in enumerate(range(self._iterations)):
            if self._verbose:
                print(f"-> iteration {i+1}/{self._iterations}", end='\r')
            self._update_linnodes_inplace()
            self._linsolve_inplace()
            self._append_structure_tracker()
            self._append_node_tracker()


    def _build_tracking_df(self) -> pd.DataFrame:
        stru_df = pd.DataFrame(self._structure_tracker)
        node_df = pd.DataFrame(self._node_tracker)
        return pd.concat([stru_df, node_df], axis=1)

    
    def _update_nodes_only(self, table:pd.DataFrame) -> pd.DataFrame:
        table_onlyUpdates = table.loc[
            :, table.iloc[0, :] != table.iloc[-1, :]
        ]
        return table_onlyUpdates
    

    def printStructureTable(self) -> None:
        """
        Print the structure table.

        This method calls the printTable method of the structure object
        to display its current state.

        Returns
        -------
        None
        """
        self._structure.printTable()

    
    def printResultTable(self) -> None:
        """
        Print the result table after linear solving.

        This method creates a new LinSolve object with the current structure
        and forces, then prints its result table.

        Returns
        -------
        None
        """
        sol = LinSolve(
            self._structure,
            self._x_force,
            self._y_force
        )
        sol.printTable()


    def printIterationTable(self) -> None:
        """
        Print the table of updates across iterations.

        This method prints the _table_onlyUpdates attribute, which contains
        only the data that changed across iterations.

        Returns
        -------
        None
        """
        print(self._table_onlyUpdates)


    def _main(self) -> None:

        self._linsolve_inplace()
        self._iterate()

        self._table = self._build_tracking_df()
        self._table_onlyUpdates = self._update_nodes_only(self._table)
        
    


