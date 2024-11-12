import pandas as pd
import numpy as np

from horloadist.zbeam import ZBeamElement
from horloadist.node import XYSupportNode
from horloadist.linsolve import LinSolve
from horloadist.loads import Load
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
            z_space:np.ndarray,
            f_x_vec:np.ndarray,
            f_y_vec:np.ndarray,
            ) -> None:

        self._linsolve = linsolve
        self._structure = linsolve._structure
        self._z_space = z_space
        self._f_x_vec = f_x_vec
        self._f_y_vec = f_y_vec


    
    @property
    def _glo_x_stiffc_cords(self) -> pd.Series:
        x_cord = self._linsolve._structure._glo_stiff_centre_x
        x_cords = np.full_like(self._z_space, x_cord)
        return pd.Series(x_cords)
    
    @property
    def _glo_y_stiffc_cords(self) -> pd.Series:
        y_cord = self._linsolve._structure._glo_stiff_centre_y
        y_cords = np.full_like(self._z_space, y_cord)
        return pd.Series(y_cords)
    
    @property
    def _glo_x_massc_cords(self) -> pd.Series:
        x_cord = self._linsolve._structure._glo_mass_centre_x
        x_cords = np.full_like(self._z_space, x_cord)
        return pd.Series(x_cords)
    
    @property
    def _glo_y_massc_cords(self) -> pd.Series:
        y_cord = self._linsolve._structure._glo_mass_centre_y
        y_cords = np.full_like(self._z_space, y_cord)
        return pd.Series(y_cords)
    

    def _build_node_F_vecs(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        num_nodes = len(self._structure._nodes)
        num_force = len(self._f_x_vec)

        Fx = np.zeros((num_force, num_nodes))
        Fy = np.zeros((num_force, num_nodes))
        Fz = np.zeros((num_force, num_nodes))

        for row, (fx, fy) in enumerate(zip(self._f_x_vec, self._f_y_vec)):
            sol = LinSolve(self._linsolve._structure, Load(fx, fy))
            for col, node in enumerate(sol._structure._nodes):
                Fx[row, col] = sol._extract_glo_f_x(node)
                Fy[row, col] = sol._extract_glo_f_y(node)
                Fz[row, col] = -self._linsolve._extract_glo_f_z(node)

        return Fx.T, Fy.T, Fz.T # vec for every node


    @property
    def pseudo_beams(self) -> list[ZBeamElement]:
        """
        Create pseudo Z-beam elements for all nodes in the structure.

        Returns
        -------
        list[ZBeamElement]
            List of ZBeamElement objects created for each node in the structure.
        """
        
        Fx, Fy, Fz = self._build_node_F_vecs()

        pseudo_beams = []
        for col, node in enumerate(self._linsolve._structure._nodes):

            ps_beam = ZBeamElement(
                node=node,
                z_space=self._z_space,
                f_x_vec=Fx[col],
                f_y_vec=Fy[col],
                f_z_vec=Fz[col],
            )

            pseudo_beams.append(ps_beam)

        return pseudo_beams
    

    def to_plotly(
            self,
            tot_fx_scale:float=1.00,
            tot_fy_scale:float=1.00,
            fx_scale:float=1.00,
            fy_scale:float=1.00,
            fz_scale:float=1.00,
            vx_scale:float=1.00,
            vy_scale:float=1.00,
            vz_scale:float=1.00,
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
            plotly_conv.to_go_x_force(fig, beam, scale=fx_scale)
            plotly_conv.to_go_y_force(fig, beam, scale=fy_scale)
            plotly_conv.to_go_z_force(fig, beam, scale=fz_scale)
            plotly_conv.to_go_x_shear(fig, beam, scale=vx_scale)
            plotly_conv.to_go_y_shear(fig, beam, scale=vy_scale)
            plotly_conv.to_go_z_normf(fig, beam, scale=vz_scale)
            plotly_conv.to_go_x_moments(fig, beam, scale=mx_scale)
            plotly_conv.to_go_y_moments(fig, beam, scale=my_scale)


        for z in self._z_space:
            
            if isinstance(polygon, Polygon):
                plotly_conv.to_go_polygon(fig, polygon, z=z)

            if isinstance(polygon, Polygons):
                plotly_conv.to_go_polygons(fig, polygon, z=z)

        
        plotly_conv.to_go_3dLine(
            fig=fig,
            x=self._glo_x_stiffc_cords,
            y=self._glo_y_stiffc_cords,
            z=pd.Series(self._z_space),
            name='stiffc',
            kwargs=plotly_conv.STIFFC_STYLE
        )

        plotly_conv.to_go_3dLine(
            fig=fig,
            x=self._glo_x_massc_cords,
            y=self._glo_y_massc_cords,
            z=pd.Series(self._z_space),
            name='massc',
            kwargs=plotly_conv.MASSC_STYLE
        )

        plotly_conv.to_go_massc_x_force(
            fig,
            glo_x=self._glo_x_massc_cords.to_numpy(),
            glo_y=self._glo_y_massc_cords.to_numpy(),
            glo_z=self._z_space,
            f_x_vec=self._f_x_vec,
            scale=tot_fx_scale
        )

        plotly_conv.to_go_massc_y_force(
            fig,
            glo_x=self._glo_x_massc_cords.to_numpy(),
            glo_y=self._glo_y_massc_cords.to_numpy(),
            glo_z=self._z_space,
            f_y_vec=self._f_y_vec,
            scale=tot_fy_scale
        )


        plotly_conv.write_html(fig, **kwargs)