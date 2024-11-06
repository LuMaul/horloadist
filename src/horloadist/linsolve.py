import pandas as pd
from typing import Literal

from horloadist.node import SupportNode
from horloadist.polygon import Polygon
from horloadist.structure import Stucture
from horloadist.loads import XYLoad

import horloadist.converters.to_rfem as rfem_conv
import horloadist.converters.to_matplotlib as plt_conv


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

        self._result_table = self._get_results()

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


    def _get_results(self) -> pd.DataFrame:

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
            f"\n{self._result_table}\n"
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
            rx = self._result_table['Vx'].loc[self._result_table['node nr'] == node._nr]
            return float(rx.iloc[0])
        
        def extracVyByNode(node:SupportNode) -> float:
            ry = self._result_table['Vy'].loc[self._result_table['node nr'] == node._nr]
            return float(ry.iloc[0])

        for node in self._structure._linnodes:
            node._Rx = -extracVxByNode(node)
            node._Ry = -extracVyByNode(node)


    def to_rfem(self, polygon:Polygon, **rfem_model_kwargs) -> None:
        """
        Convert the current structure to RFEM model format and create corresponding elements.
        
        Creates support nodes, shell elements, and free loads in RFEM based on the current
        structure configuration.
        
        Parameters
        ----------
        polygon : Polygon
            The polygon object representing the structure's geometry.
        **rfem_model_kwargs : dict
            Additional keyword arguments to pass to the RFEM model initialization.
            
        Returns
        -------
        None
        
        Notes
        -----
        This method performs the following operations:
        1. Initializes the RFEM model
        2. Creates support nodes for all structure nodes
        3. Converts the polygon to RFEM shell elements
        4. Applies free loads at the specified locations
        """
        shell_tag = self._structure.to_rfem(
            polygon=polygon,
            finish_mod=False,
            **rfem_model_kwargs
            )

        glo_x, glo_y = polygon.centroid
        rfem_conv.to_rfem_free_load(glo_x, glo_y, shell_tag, self._load)

        rfem_conv.Model.clientModel.service.finish_modification()

        rfem_conv.Calculate_all()

        self._result_table['RFEM Vx'] = rfem_conv.from_rfem_XForces(self._structure._node_numbers)
        self._result_table['RFEM Vy'] = rfem_conv.from_rfem_YForces(self._structure._node_numbers)

        


    def to_mpl(
            self,
            polygon:Polygon,
            name:str='',
            show:bool=True,
            save:bool=False,
            fformat:str='pdf',
            forces:Literal['sum', 'torsion', 'transl', 'none']='sum',
            fscale:float=1,
            **suplot_kwargs
            ) -> tuple[plt_conv.mpl_fig.Figure, plt_conv.mpl_axes.Axes]:
        """
        Create a matplotlib visualization of the structure and its forces.
        
        Parameters
        ----------
        polygon : Polygon
            The polygon object representing the structure's geometry.
        name : str, optional
            Name of the plot, by default ''.
        show : bool, optional
            Whether to display the plot, by default True.
        save : bool, optional
            Whether to save the plot to a file, by default False.
        fformat : str, optional
            File format for saving the plot, by default 'pdf'.
        forces : {'sum', 'torsion', 'transl', 'none'}, optional
            Type of forces to display:
            - 'sum': Show total resultant forces
            - 'torsion': Show torsional forces
            - 'transl': Show translational forces
            - 'none': Don't show forces
            By default 'sum'.
        fscale : float, optional
            Scaling factor for force vectors, by default 1.
            Larger values make forces appear smaller.
        **suplot_kwargs : dict
            Additional keyword arguments to pass to the subplot creation.
            
        Returns
        -------
        tuple[Figure, Axes]
            Matplotlib figure and axes objects containing the visualization.
            
        Notes
        -----
        The visualization includes:
        - The structure geometry
        - Force vectors at the mass center (in dark red)
        - Force vectors at nodes (in red) based on the selected force type
        """
        fig, ax = self._structure.to_mpl(polygon, name, show=False, save=False, **suplot_kwargs)

        plt_conv.to_plt_force(
            ax,
            self._structure._glo_mass_centre_x,
            self._structure._glo_mass_centre_y,
            x_magnitude=self._load._x_magnitude,
            y_magnitude=self._load._y_magnitude,
            scale=1/fscale,
            color='blue',
            )
        
        if forces == 'sum':
            plt_conv.to_plt_force(
                ax,
                self._structure._glo_node_x,
                self._structure._glo_node_y,
                self._node_final_Vx,
                self._node_final_Vy,
                scale=1/fscale,
                color='red'
            )

        elif forces == 'torsion':
            plt_conv.to_plt_force(
                ax,
                self._structure._glo_node_x,
                self._structure._glo_node_y,
                self._node_Ts_from_EIwx,
                self._node_Ts_from_EIwy,
                scale=1/fscale,
                color='red'
            )

        elif forces == 'transl':
            plt_conv.to_plt_force(
                ax,
                self._structure._glo_node_x,
                self._structure._glo_node_y,
                self._node_Vx_from_EIx,
                self._node_Vy_from_EIy,
                scale=1/fscale,
                color='red'
            )

        if save:
            kwargs = {'format':fformat}
            plt_conv.to_file(**kwargs)
        
        if show:
            plt_conv.plt.show()

        return fig, ax