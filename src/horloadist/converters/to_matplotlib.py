import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.axes as mpl_axes
import matplotlib.figure as mpl_fig
import matplotlib.patches as mpl_patches

from horloadist.node import SupportNode
from horloadist.polygon import Polygon

STYLE_SETTINGS = {
    'node_rect_width':0.10,
    'node_rect_heigt':0.10,
    'node_fontsize':5,
    'fig_buffer':1.00,
}

def init_plt(name:str='', **suplot_kwargs) -> tuple[mpl_fig.Figure, mpl_axes.Axes]:
    fig, ax = plt.subplots(**suplot_kwargs)
    ax:mpl_axes.Axes = ax
    if name:
        fig.suptitle(name)
    return fig, ax


def get_plt_size(
        ax:mpl_axes.Axes,
        glo_node_x:pd.Series,
        glo_node_y:pd.Series,
        polygon:Polygon
        ) -> None:
    
    BUFFER = STYLE_SETTINGS['fig_buffer']
    x_nd_min, x_nd_max = glo_node_x.min()-BUFFER, glo_node_x.max()+BUFFER
    y_nd_min, y_nd_max = glo_node_y.min()-BUFFER, glo_node_y.max()+BUFFER

    x_vals = [x for (x, _) in polygon._xy]
    y_vals = [y for (_, y) in polygon._xy]
    x_pg_min, x_pg_max = min(x_vals), max(x_vals)
    y_pg_min, y_pg_max = min(y_vals), max(y_vals)

    glo_x_minmax = min((x_nd_min, x_pg_min)), max((x_nd_max, x_pg_max))
    glo_y_minmax = min((y_nd_min, y_pg_min)), max((y_nd_max, y_pg_max))
    
    ax.set_xlim(*glo_x_minmax)
    ax.set_ylim(*glo_y_minmax)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks(list(np.arange(int(glo_x_minmax[0]), int(glo_x_minmax[1]) + 1, 1.00)))
    ax.set_yticks(list(np.arange(int(glo_y_minmax[0]), int(glo_y_minmax[1]) + 1, 1.00)))
    ax.grid(color='gray', linestyle=':', linewidth=0.5)



def to_plt_node(ax:mpl_axes.Axes, node:SupportNode) -> None:

    rect = mpl_patches.Rectangle(
        xy=(node._glo_x, node._glo_y),
        width=STYLE_SETTINGS['node_rect_width'],
        height=STYLE_SETTINGS['node_rect_heigt'],
        color='black',
        zorder=3,
        )
    
    center_x = node._glo_x + STYLE_SETTINGS['node_rect_width']
    center_y = node._glo_y + STYLE_SETTINGS['node_rect_heigt']

    ax.text(
        center_x,
        center_y,
        str(node._nr),
        ha='left',
        va='bottom',
        color='black',
        fontsize=STYLE_SETTINGS['node_fontsize'],
        zorder=2,
    )
    
    ax.add_patch(rect)


def to_plt_polygon(ax:mpl_axes.Axes, polygon:Polygon) -> None:
    poly = mpl_patches.Polygon(
        xy=polygon._xy,
        closed=True,
        color='black',
        fc='lightgray',
        alpha=0.5,
        zorder=0
        )

    ax.add_patch(poly)