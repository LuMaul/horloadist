import pandas as pd
import numpy as np

from horloadist.zbeam import ZBeamElement
from horloadist.node import XYSupportNode
from horloadist.linsolve import LinSolve
from horloadist.polygon import Polygon, Polygons

import horloadist.converters.to_plotly as plotly_conv


class ZLinSolve:
    """
    A class for performing pseudo-3D structural analysis based on linear solution results.

    This class extends 2D linear analysis results into 3D by creating pseudo Z-beam
    elements at support nodes.

    Parameters
    ----------
    linsolve : LinSolve
        Linear solution object containing 2D analysis results.
    z_num_floors : int, optional
        Number of floors in the Z direction, by default 5.
    z_floor_heigt : float, optional
        Height of each floor, by default 3.00.

    Attributes
    ----------
    _linsolve : LinSolve
        Reference to the linear solution object.
    _result_table : pd.DataFrame
        Results table from linear solution.
    _z_num_floors : int
        Number of floors.
    _z_floor_heigt : float
        Height of each floor.
    """
    def __init__(
            self,
            linsolve:LinSolve,
            z_num_floors:int=5,
            z_floor_heigt:float=3.00,
            ) -> None:

        self._linsolve = linsolve
        self._result_table = self._linsolve._result_table
        self._z_num_floors = z_num_floors
        self._z_floor_heigt = z_floor_heigt

    @property
    def _z_heigt(self) -> float:
        return self._z_num_floors * self._z_floor_heigt

    @property
    def _glo_z_shell_cords(self) -> pd.Series:
        z_cords = np.linspace(
            start=self._z_floor_heigt,
            stop=self._z_heigt,
            num=self._z_num_floors
            )
        return pd.Series(z_cords)
    
    @property
    def _glo_z_cords(self) -> pd.Series:
        z_cords = np.linspace(
            start=0.00,
            stop=self._z_heigt,
            num=self._z_num_floors
        )
        return pd.Series(z_cords)
    
    @property
    def _glo_x_stiffc_cords(self) -> pd.Series:
        x_cord = self._linsolve._structure._glo_stiff_centre_x
        x_cords = np.full_like(self._glo_z_cords, x_cord)
        return pd.Series(x_cords)
    
    @property
    def _glo_y_stiffc_cords(self) -> pd.Series:
        y_cord = self._linsolve._structure._glo_stiff_centre_y
        y_cords = np.full_like(self._glo_z_cords, y_cord)
        return pd.Series(y_cords)
    
    @property
    def _glo_x_massc_cords(self) -> pd.Series:
        x_cord = self._linsolve._structure._glo_mass_centre_x
        x_cords = np.full_like(self._glo_z_cords, x_cord)
        return pd.Series(x_cords)
    
    @property
    def _glo_y_massc_cords(self) -> pd.Series:
        y_cord = self._linsolve._structure._glo_mass_centre_y
        y_cords = np.full_like(self._glo_z_cords, y_cord)
        return pd.Series(y_cords)


    def _extract_glo_f_x(self, node:XYSupportNode) -> float:
        f_x = self._result_table['Vx'].loc[self._result_table['node nr'] == node._nr]
        return float(f_x.iloc[0])

    def _extract_glo_f_y(self, node:XYSupportNode) -> float:
        f_y = self._result_table['Vy'].loc[self._result_table['node nr'] == node._nr]
        return float(f_y.iloc[0])


    def _extract_glo_f_z(self, node:XYSupportNode) -> float:
        if 'RFEM Vz' in self._result_table:
            f_z = self._result_table['RFEM Vz'].loc[
                self._result_table['node nr'] == node._nr
                ]
            return float(f_z.iloc[0])
        else:
            return 0.0

    @property
    def pseudo_beams(self) -> list[ZBeamElement]:
        """
        Create pseudo Z-beam elements for all nodes in the structure.

        Returns
        -------
        list[ZBeamElement]
            List of ZBeamElement objects created for each node in the structure.
        """
        pseudo_beams = []
        for node in self._linsolve._structure._nodes:
            ps_beam = ZBeamElement(
                node=node,
                z_num_floors=self._z_num_floors,
                z_floor_heigt=self._z_floor_heigt,
                const_f_x=self._extract_glo_f_x(node),
                const_f_y=self._extract_glo_f_y(node),
                const_f_z=self._extract_glo_f_z(node),
            )
            pseudo_beams.append(ps_beam)
        return pseudo_beams
    

    def to_plotly(
            self,
            fx_scale:float=1.00,
            fy_scale:float=1.00,
            fz_scale:float=1.00,
            mx_scale:float=1.00,
            my_scale:float=1.00,
            polygon:Polygon|Polygons|None=None,
            **kwargs
            ) -> None:
        """
        Generates a Plotly 3D figure to visualize pseudo Z-beam elements with force and moment scaling.

        Parameters
        ----------
        fx_scale : float, optional
            Scaling factor for forces in the x-direction (default is 1.00).
        fy_scale : float, optional
            Scaling factor for forces in the y-direction (default is 1.00).
        fz_scale : float, optional
            Scaling factor for normal forces in the z-direction (default is 1.00).
        mx_scale : float, optional
            Scaling factor for moments around the x-axis (default is 1.00).
        my_scale : float, optional
            Scaling factor for moments around the y-axis (default is 1.00).
        polygon : Polygon, Polygons, or None, optional
            Polygonal representation(s) of 3D elements to add to the figure.
            Accepts a single `Polygon`, multiple `Polygons`, or None for no polygons.
        **kwargs : dict, optional
            Additional keyword arguments for customizing Plotly figure export, such as
            `file` for HTML export or styling options.

        Returns
        -------
        None
            This function modifies the figure in place and does not return a value.
            The generated Plotly figure is saved or displayed as an HTML file based
            on parameters passed in **kwargs.

        Notes
        -----
        This function uses the `plotly_conv` module to initialize a 3D Plotly figure,
        which visualizes the properties of pseudo Z-beam elements in the structure.
        It includes the following graphical elements:
        
        - Pseudo Z-beam geometries (lines connecting beam nodes).
        - X and Y shear forces, and Z normal forces, scaled by `fx_scale`, `fy_scale`,
        and `fz_scale`, respectively.
        - Moments around X and Y axes, scaled by `mx_scale` and `my_scale`.
        - Optional polygonal shells based on `polygon` argument.
        - 3D lines representing stiffness (`stiffc`) and mass centerlines (`massc`).
        
        After constructing the figure, it is exported to an HTML file if `filename` 
        or other file-saving options are specified in `kwargs`.
        """
        fig = plotly_conv.init_go()
        for beam in self.pseudo_beams:
            plotly_conv.to_go_beam(fig, beam)
            plotly_conv.to_go_x_shear(fig, beam, scale=fx_scale)
            plotly_conv.to_go_y_shear(fig, beam, scale=fy_scale)
            plotly_conv.to_go_z_normf(fig, beam, scale=fz_scale)
            plotly_conv.to_go_x_moments(fig, beam, scale=mx_scale)
            plotly_conv.to_go_y_moments(fig, beam, scale=my_scale)


        for z in self._glo_z_shell_cords:
            if isinstance(polygon, Polygon):
                plotly_conv.to_go_polygon(fig, polygon, z=z)

            if isinstance(polygon, Polygons):
                plotly_conv.to_go_polygons(fig, polygon, z=z)

        
        plotly_conv.to_go_3dLine(
            fig=fig,
            x=self._glo_x_stiffc_cords,
            y=self._glo_y_stiffc_cords,
            z=self._glo_z_cords,
            name='stiffc',
            kwargs=plotly_conv.STIFFC_STYLE
        )

        plotly_conv.to_go_3dLine(
            fig=fig,
            x=self._glo_x_massc_cords,
            y=self._glo_y_massc_cords,
            z=self._glo_z_cords,
            name='massc',
            kwargs=plotly_conv.MASSC_STYLE
        )
        
        plotly_conv.write_html(fig, **kwargs)