import pandas as pd
import numpy as np
from copy import deepcopy


from horloadist.polygon import Polygon
from horloadist.stiffnesses import KX, KY
from horloadist.node import SupportNode
from horloadist.utils import interpolateXY

import horloadist.converters.io_rfem as rfem_conv
import horloadist.converters.to_matplotlib as plt_conv


class Stucture:
    """
    Structure class for managing the geometric and stiffness properties of a structural system.

    Parameters
    ----------
    nodes : list[SupportNode]
        List of SupportNode objects representing the nodes in the structure.
    glo_mass_centre : tuple[float, float] or np.ndarray
        Global mass center coordinates [x, y].
    verbose : bool, optional
        Flag indicating whether to print verbose information. Defaults to True.

    Attributes
    ----------
    _nodes : list[SupportNode]
        List of SupportNode objects representing the nodes in the structure.
    _glo_mass_centre : np.ndarray
        Numpy array containing the global mass center coordinates [x, y].
    _verbose : bool
        Flag indicating whether to print verbose information.
    _linnodes : list[SupportNode]
        List of linear SupportNode objects.
    _node_numbers : pd.Series
        Series of node numbers.
    _glo_node_x : pd.Series
        Series of global x-coordinates of the nodes.
    _glo_node_y : pd.Series
        Series of global y-coordinates of the nodes.
    _loc_node_x : pd.Series
        Series of local x-coordinates of the nodes.
    _loc_node_y : pd.Series
        Series of local y-coordinates of the nodes.
    _node_EIy : pd.Series
        Series of EIy values for the nodes.
    _node_EIx : pd.Series
        Series of EIx values for the nodes.
    _loc_stiff_centre : np.ndarray
        Numpy array containing the local stiffness center coordinates [x, y].
    _glo_stiff_centre : np.ndarray
        Numpy array containing the global stiffness center coordinates [x, y].
    _loc_node_xs : pd.Series
        Series of local x-coordinates of the nodes relative to the stiffness center.
    _loc_node_ys : pd.Series
        Series of local y-coordinates of the nodes relative to the stiffness center.
    _node_EIx_proportion : pd.Series
        Series of the proportion of EIx for each node.
    _node_EIy_proportion : pd.Series
        Series of the proportion of EIy for each node.
    _global_EIw : pd.Series
        Series of the global warping stiffness.
    _node_EIwx_proportion : pd.Series
        Series of the proportion of EIwx for each node.
    _node_EIwy_proportion : pd.Series
        Series of the proportion of EIwy for each node.
    _result_table : pd.DataFrame
        DataFrame containing the detailed summary of the structure's geometric and stiffness properties.

    Methods
    -------
    _to_linear_nodes(nodes: list[SupportNode]) -> list[SupportNode]
        Converts the input nodes to a list of linear SupportNode objects.
    printTable() -> None
        Prints a detailed summary of the structure's geometric and stiffness properties.
    to_rfem(polygon: Polygon, **rfem_model_kwargs) -> None
        Exports the structure to an RFEM model.
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
            if isinstance(node._glo_EIx, pd.DataFrame):
                node._glo_EIx = interpolateXY(node._glo_EIx, MOMENTUM)
                printInfo(node._nr, 'x', node._glo_EIx)
            if isinstance(node._glo_EIy, pd.DataFrame):
                node._glo_EIy = interpolateXY(node._glo_EIy, MOMENTUM)
                printInfo(node._nr, 'y', node._glo_EIy)
            return node
        
        return [extractStiffnessAtMomentZero(node) for node in nodes]
    

    @property
    def _node_numbers(self) -> pd.Series:
        return pd.Series([node._nr for node in self._linnodes])
    
    @property
    def _glo_node_x(self) -> pd.Series:
        return pd.Series([node._glo_x for node in self._linnodes])

    @property
    def _glo_node_y(self) -> pd.Series:
        return pd.Series([node._glo_y for node in self._linnodes])
    
    @property
    def _loc_node_x(self) -> pd.Series:
        return self._glo_node_x - self._glo_mass_centre_x
    
    @property
    def _loc_node_y(self) -> pd.Series:
        return self._glo_node_y - self._glo_mass_centre_y

    @property
    def _node_EIy(self) -> pd.Series:
        return pd.Series([node._glo_EIy for node in self._linnodes])
    
    @property
    def _node_EIx(self) -> pd.Series:
        return pd.Series([node._glo_EIx for node in self._linnodes])
    
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
        

    def to_rfem(self, polygon:Polygon, finish_mod=True, **rfem_model_kwargs) -> int:
        """
        Initializes an RFEM model and converts nodes and polygons to RFEM format.

        Parameters
        ----------
        polygon : Polygon
            A polygon object defining the geometry to be converted to RFEM.
        **rfem_model_kwargs : dict, optional
            Additional keyword arguments to initialize the RFEM model. These may include parameters
            for model setup, boundary conditions, or other RFEM-specific configurations.

        Returns
        -------
        None
            This method does not return a value. It modifies the RFEM model by adding nodes and a shell
            representation based on the input polygon.

        Notes
        -----
        This function initializes the RFEM model using the provided keyword arguments, then iterates
        over `self._nodes`, converting each node into an RFEM support node. The polygon is added as
        an RFEM shell. Some additional steps, such as beginning and finishing the RFEM model
        modification and calculating the model, are currently commented out.
        """
        rfem_conv.init_rfem_model(**rfem_model_kwargs)
        
        rfem_conv.Model.clientModel.service.begin_modification()

        for node in self._nodes:
            rfem_conv.to_rfem_support_node(node=node)

        shell_tag = rfem_conv.to_rfem_shell(polygon)

        if finish_mod:        
            rfem_conv.Model.clientModel.service.finish_modification()

        return shell_tag



    def to_mpl(
            self,
            polygon:Polygon,
            name:str='',
            show:bool=True,
            save:bool=False,
            fformat:str='pdf',
            **suplot_kwargs,
            ) -> tuple[plt_conv.mpl_fig.Figure, plt_conv.mpl_axes.Axes]:
        """
        Plots the polygon and node information using Matplotlib.

        Parameters
        ----------
        polygon : Polygon
            A polygon object defining the geometry to be plotted.
        name : str, optional
            Title of the plot, used as the figure name. Default is an empty string.
        show : bool, optional
            If True, displays the plot. Default is True.
        save : bool, optional
            If True, saves the plot to a file. Default is False.
        fformat : str, optional
            Format in which to save the file, if `save` is True. Default is 'pdf'.
        **suplot_kwargs : dict, optional
            Additional keyword arguments for Matplotlib subplot configuration.

        Returns
        -------
        tuple
            A tuple containing:
            - fig : plt_conv.mpl_fig.Figure
                The Matplotlib figure object.
            - ax : plt_conv.mpl_axes.Axes
                The Matplotlib axes object.

        Notes
        -----
        The function initializes a Matplotlib plot, calculates the scaling factor for stiffness
        visualization, and then plots each node with respective stiffness values in the x and y
        directions. Additional nodes for mass center and stiffness center are marked in green and
        blue, respectively. The plot is saved to a file if `save` is True and displayed if `show`
        is True.
        """
        fig, ax = plt_conv.init_plt(name=name, **suplot_kwargs)
        x_rng, y_rng = plt_conv.auto_plt_size(
            ax,
            self._glo_node_x,
            self._glo_node_y,
            polygon
            )

        plt_conv.to_plt_polygon(ax, polygon)
        
        stiff_scale = max(x_rng, y_rng) / 15 / max(self._node_EIx.max(), self._node_EIy.max())

        for node in self._nodes:
            plt_conv.to_plt_node(
                ax,
                node._glo_x,
                node._glo_y,
                str(node._nr),
                'black',
                stiff_scale,
                kx=node._glo_EIy,
                ky=node._glo_EIx,
                )

        plt_conv.to_plt_node(
            ax,
            self._glo_mass_centre_x,
            self._glo_mass_centre_y,
            f'MC ({self._glo_mass_centre_x:0.4f}, {self._glo_mass_centre_y:0.4f})',
            'green',
            stiff_scale
            )
        
        plt_conv.to_plt_node(
            ax,
            self._glo_stiff_centre_x,
            self._glo_stiff_centre_y,
            f'SC ({self._glo_stiff_centre_x:0.4f}, {self._glo_stiff_centre_y:0.4f})',
            'blue',
            stiff_scale
            )

        if save:
            kwargs = {'format':fformat}
            plt_conv.to_file(**kwargs)
        
        if show:
            plt_conv.plt.show()

        return fig, ax