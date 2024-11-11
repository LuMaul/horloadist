import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import time

import __main__

from horloadist.zbeam import ZBeamElement
from horloadist.polygon import Polygon, Polygons


ZBEAM_STYLE = {
    'line': {'color': 'black'},
    'legendgroup': 'beams',
    'legendgrouptitle_text': "Beams"
}

X_SHEAR_STYLE = {
    'line': {'color': 'orange'},
    'legendgroup' : 'xshear',
    'legendgrouptitle_text': "Global Vx"
}

Y_SHEAR_STYLE = {
    'line': {'color': 'orange'},
    'legendgroup' : 'yshear',
    'legendgrouptitle_text': "Global Vy"
}

NORMF_STYLE = {
    'line': {'color': 'orange'},
    'legendgroup' : 'normf',
    'legendgrouptitle_text': "Normforce"
}

POLY_STYLE = {
    'line': {'color': 'black'},
    'legendgroup': 'shell',
    'legendgrouptitle_text': "Shells"
}

Y_MOMENT_STYLE = {
    'line': {'color': 'orange'},
    'legendgroup' : 'ymoment',
    'legendgrouptitle_text': "Global My"
}

X_MOMENT_STYLE = {
    'line': {'color': 'orange'},
    'legendgroup' : 'xmoment',
    'legendgrouptitle_text': "Global Mx"
}

STIFFC_STYLE = {
    'line': {'color': 'blue'}
}

MASSC_STYLE = {
    'line': {'color': 'red'}
}

DEFAULT_FACE_STYLE = {
    'opacity': 0.3,
    'colorscale': [[0, 'rgb(255, 165, 0)'], [1, 'rgb(255, 165, 0)']],
    'showscale': False,
    'hoverinfo': 'skip'
}


HOVERTEMPL_X_SHEAR = '<br>Vx: %{customdata[4]:.2f}'
HOVERTEMPL_Y_SHEAR = '<br>Vy: %{customdata[5]:.2f}'
HOVERTEMPL_Y_MOMENT = '<br>My: %{customdata[6]:.2f}'
HOVERTEMPL_X_MOMENT = '<br>Mx: %{customdata[7]:.2f}'
HOVERTEMPL_NORMF = '<br>N: %{customdata[8]:.2f}'
HOVERTEMPL_XYZ_BEAM = (
    '<br>X: %{customdata[1]:.2f}'
    '<br>Y: %{customdata[2]:.2f}'
    '<br>Z: %{customdata[3]:.2f}'
)




def init_go():
    fig = go.Figure()
    fig.update_layout(template='simple_white')
    return fig


def _fill_between(
        fig: go.Figure,
        xyz_3DLine1: tuple[pd.Series, pd.Series, pd.Series],
        xyz_3DLine2: tuple[pd.Series, pd.Series, pd.Series],
        kwargs: dict = {}
        ) -> go.Figure:
    
    x1, y1, z1 = xyz_3DLine1
    x2, y2, z2 = xyz_3DLine2
    
    x = pd.concat([x1, x2], axis=1).T.values
    y = pd.concat([y1, y2], axis=1).T.values
    z = pd.concat([z1, z2], axis=1).T.values
    
    style = DEFAULT_FACE_STYLE.copy()
    style.setdefault('surfacecolor', [[1] * len(x1)] * 2)
    style.update(kwargs)
    style.pop('line', None)

    
    fig.add_trace(
        go.Surface(
            x=x,
            y=y,
            z=z,
            **style
        )
    )
    
    return fig



def to_go_3dLine(
        fig:go.Figure,
        x:pd.Series,
        y:pd.Series,
        z:pd.Series,
        name:str='',
        hovertempl:str|None=None,
        customdata:np.ndarray|None=None,
        kwargs:dict={}
        ) -> go.Figure:
    
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines',
            name=name,
            hovertemplate=hovertempl,
            customdata=customdata,
            **kwargs
        )
    )

    return fig


def to_go_fill_between(
        fig:go.Figure,

    ) -> go.Figure:

    return fig


def to_go_beam(
        fig:go.Figure,
        zbeam:ZBeamElement
        ) -> go.Figure:
    
    to_go_3dLine(
        fig,
        x=zbeam._glo_x_cords,
        y=zbeam._glo_y_cords,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} beam',
        customdata=zbeam._result_table.values,
        hovertempl=HOVERTEMPL_XYZ_BEAM,
        kwargs=ZBEAM_STYLE
    )
    
    return fig


def to_go_x_shear(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    x_vals = zbeam._glo_x_cords + zbeam._glo_x_shear * scale

    to_go_3dLine(
        fig=fig,
        x=x_vals,
        y=zbeam._glo_y_cords,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} glo Vx',
        hovertempl=HOVERTEMPL_X_SHEAR,
        customdata=zbeam._result_table.values,
        kwargs=X_SHEAR_STYLE
    )

    xyz1 = zbeam._glo_x_cords, zbeam._glo_y_cords, zbeam._glo_z_cords
    xyz2 = x_vals, zbeam._glo_y_cords, zbeam._glo_z_cords
    _fill_between(fig, xyz1, xyz2, X_SHEAR_STYLE)

    return fig



def to_go_y_shear(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    y_vals = zbeam._glo_y_cords + zbeam._glo_y_shear * scale

    to_go_3dLine(
        fig=fig,
        x=zbeam._glo_x_cords,
        y=y_vals,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} glo Vy',
        customdata=zbeam._result_table.values,
        hovertempl=HOVERTEMPL_Y_SHEAR,
        kwargs=Y_SHEAR_STYLE
    )

    xyz1 = zbeam._glo_x_cords, zbeam._glo_y_cords, zbeam._glo_z_cords
    xyz2 = zbeam._glo_x_cords, y_vals, zbeam._glo_z_cords
    _fill_between(fig, xyz1, xyz2, Y_SHEAR_STYLE)

    return fig


def to_go_z_normf(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    x_vals = zbeam._glo_x_cords + zbeam._glo_z_normf * scale

    to_go_3dLine(
        fig=fig,
        x=x_vals,
        y=zbeam._glo_y_cords,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} Normf',
        customdata=zbeam._result_table.values,
        hovertempl=HOVERTEMPL_NORMF,
        kwargs=NORMF_STYLE
    )

    xyz1 = zbeam._glo_x_cords, zbeam._glo_y_cords, zbeam._glo_z_cords
    xyz2 = x_vals, zbeam._glo_y_cords, zbeam._glo_z_cords
    _fill_between(fig, xyz1, xyz2, NORMF_STYLE)

    return fig


def to_go_y_moments(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    x_vals = zbeam._glo_x_cords + zbeam._glo_y_moments * scale

    to_go_3dLine(
        fig=fig,
        x=x_vals,
        y=zbeam._glo_y_cords,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} glo My',
        customdata=zbeam._result_table.values,
        hovertempl=HOVERTEMPL_Y_MOMENT,
        kwargs=Y_MOMENT_STYLE
    )

    xyz1 = zbeam._glo_x_cords, zbeam._glo_y_cords, zbeam._glo_z_cords
    xyz2 = x_vals, zbeam._glo_y_cords, zbeam._glo_z_cords
    _fill_between(fig, xyz1, xyz2, Y_MOMENT_STYLE)

    return fig


def to_go_x_moments(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    y_vals = zbeam._glo_y_cords + zbeam._glo_x_moments * scale

    to_go_3dLine(
        fig=fig,
        x=zbeam._glo_x_cords,
        y=y_vals,
        z=zbeam._glo_z_cords,
        name=f'{zbeam._no} glo Mx',
        customdata=zbeam._result_table.values,
        hovertempl=HOVERTEMPL_X_MOMENT,
        kwargs=X_MOMENT_STYLE
    )

    xyz1 = zbeam._glo_x_cords, zbeam._glo_y_cords, zbeam._glo_z_cords
    xyz2 = zbeam._glo_x_cords, y_vals, zbeam._glo_z_cords
    _fill_between(fig, xyz1, xyz2, X_MOMENT_STYLE)

    return fig


def to_go_polygon(
        fig:go.Figure,
        polygon:Polygon,
        z:float=0.0,
        name:str='',
        ) -> go.Figure:

    x1, y1 = np.array(polygon._xy_closed_polygon).T
    z1 = np.full_like(x1, z)

    to_go_3dLine(
        fig=fig,
        x=x1,
        y=y1,
        z=z1,
        name=f'{z=:0.3f} '+name,
        kwargs=POLY_STYLE
    )

    return fig


def to_go_polygons(fig:go.Figure, polygons:Polygons, z:float=0.0) -> go.Figure:

    to_go_polygon(fig, polygons._pos_polygon, z=z, name='pos poly')
    
    for neg_poly in polygons._neg_polygons:
        to_go_polygon(fig, neg_poly, z=z, name='neg poly')

    return fig


def write_html(fig:go.Figure, **kwargs) -> None:

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    fname = f'{os.path.basename(__main__.__file__)}_{timestamp}.html'
    kwargs.setdefault('file', fname)

    kwargs.setdefault('auto_open', True)
    
    fig.write_html(**kwargs)