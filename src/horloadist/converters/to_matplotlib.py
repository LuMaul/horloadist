import pandas as pd
import numpy as np
import os

import __main__

import matplotlib.pyplot as plt
import matplotlib.axes as mpl_axes
import matplotlib.figure as mpl_fig
import matplotlib.patches as mpl_patches

from horloadist.node import SupportNode
from horloadist.polygon import Polygon

NODE_STIFF_LEN = 1.00

GRID_STYLING = {
    'color':'gray',
    'linestyle':':',
    'linewidth':0.5,
    'zorder':2,
}

NODE_STYLING = {
    'width':0.05,
    'height':0.05,
    'zorder':3,
}

NODE_FONT_STYLING = {
    'ha':'left',
    'va':'bottom',
    'fontsize':8,
    'zorder':4,
}

STIFF_LINE_STYLING = {
    'color':'black',
    'linewidth':1,
}


POLYGON_STYLING = {
    'color':'black',
    'fc':'lightgray',
    'alpha':0.3,
    'zorder':0,
}

FORCE_STYLING = {
    'linewidth':0.5,
    'angles':'xy',
    'scale_units':'xy',
    'width':0.0015,
    'zorder':5
}

FORCE_FONT_STYLING = {
    'ha':'right',
    'va':'top',
    'fontsize':8,
    'zorder':4,
}

def init_plt(name:str='', **suplot_kwargs) -> tuple[mpl_fig.Figure, mpl_axes.Axes]:
    suplot_kwargs.setdefault('figsize', (15, 10))
    fig, ax = plt.subplots(**suplot_kwargs)
    ax:mpl_axes.Axes = ax
    if name:
        fig.suptitle(name)
    fig.tight_layout(pad=3)
    return fig, ax


def auto_plt_size(
        ax:mpl_axes.Axes,
        glo_node_x:pd.Series,
        glo_node_y:pd.Series,
        polygon:Polygon
        ) -> tuple:
    
    BUFFER = 1.00
    x_nd_min, x_nd_max = glo_node_x.min()-BUFFER, glo_node_x.max()+BUFFER
    y_nd_min, y_nd_max = glo_node_y.min()-BUFFER, glo_node_y.max()+BUFFER

    x_vals = [x for (x, _) in polygon._xy]
    y_vals = [y for (_, y) in polygon._xy]
    x_pg_min, x_pg_max = min(x_vals)-BUFFER, max(x_vals)+BUFFER
    y_pg_min, y_pg_max = min(y_vals)-BUFFER, max(y_vals)+BUFFER

    glo_x_min, glo_x_max = min((x_nd_min, x_pg_min)), max((x_nd_max, x_pg_max))
    glo_y_min, glo_y_max = min((y_nd_min, y_pg_min)), max((y_nd_max, y_pg_max))
    
    ax.set_xlim(glo_x_min, glo_x_max)
    ax.set_ylim(glo_y_min, glo_y_max)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks(list(np.arange(int(glo_x_min), int(glo_x_max) + 1, 1.00)))
    ax.set_yticks(list(np.arange(int(glo_y_min), int(glo_y_max) + 1, 1.00)))
    ax.grid(**GRID_STYLING)

    x_rng = abs(glo_x_min - glo_x_max)
    y_rng = abs(glo_y_min - glo_y_max)

    return x_rng, y_rng


def to_plt_node(
        ax:mpl_axes.Axes,
        x:float,
        y:float,
        text:str='',
        color:str='black',
        stiff_scale:float=1.00,
        kx:float=0,
        ky:float=0
        ) -> None:

    dx = NODE_STYLING['width'] / 2
    dy = NODE_STYLING['height'] / 2

    rect = mpl_patches.Rectangle(
        xy=(x-dx, y-dy),
        color=color,
        **NODE_STYLING
        )
    
    ax.add_patch(rect)

    center_x = x + dx
    center_y = y + dy

    ax.text(
        x=center_x,
        y=center_y,
        s=text,
        color=color,
        **NODE_FONT_STYLING
    )

    dx, dy = kx * stiff_scale, ky * stiff_scale

    ax.hlines(y=y, xmin=x-dx, xmax=x+dx, **STIFF_LINE_STYLING)
    ax.vlines(x=x, ymin=y-dy, ymax=y+dy, **STIFF_LINE_STYLING)

    
def to_plt_polygon(ax:mpl_axes.Axes, polygon:Polygon) -> None:
    poly = mpl_patches.Polygon(
        xy=polygon._xy,
        closed=True,
        **POLYGON_STYLING
        )

    ax.add_patch(poly)


def to_plt_force(
    ax: mpl_axes.Axes,
    glo_x: int|float|list|np.ndarray|pd.Series,
    glo_y: int|float|list|np.ndarray|pd.Series,
    x_magnitude: int|float|list|np.ndarray|pd.Series,
    y_magnitude: int|float|list|np.ndarray|pd.Series,
    scale: int|float = 1.00,
    color: str = 'b',
) -> None:
    
    def to_array(x: int|float|list|np.ndarray|pd.Series) -> np.ndarray:
        if isinstance(x, (float, int)):
            return np.array([x])
        elif isinstance(x, (list, tuple)):
            return np.array(x)
        elif isinstance(x, pd.Series):
            return x.to_numpy()
        elif isinstance(x, np.ndarray):
            return x
        else:
            raise TypeError(f"Unsupported type: {type(x)}")
    
    glo_x_arr = to_array(glo_x)
    glo_y_arr = to_array(glo_y)
    x_mag_arr = to_array(x_magnitude)
    y_mag_arr = to_array(y_magnitude)
    
    lengths = [len(arr) for arr in [glo_x_arr, glo_y_arr, x_mag_arr, y_mag_arr]]
    if not all(length == lengths[0] for length in lengths):
        raise ValueError("All input sequences must have the same length")
    
    FORCE_STYLING.setdefault('scale', scale)
    
    ax.quiver(glo_x_arr, glo_y_arr, x_mag_arr, y_mag_arr, color=color, **FORCE_STYLING)
    
    texts = [
        f'({x:.4f}, {y:.4f})'
        for x, y in zip(x_mag_arr, y_mag_arr)
    ]
    
    for x, y, text in zip(glo_x_arr, glo_y_arr, texts):
        ax.text(
            x=x,
            y=y,
            s=text,
            color=color,
            **FORCE_FONT_STYLING
        )


def to_file(**kwargs) -> None:
    kwargs.setdefault('format', 'pdf')
    kwargs.setdefault('fname', f'{os.path.basename(__main__.__file__)}.{kwargs['format']}')
    plt.savefig(**kwargs)