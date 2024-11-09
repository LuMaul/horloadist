import plotly.graph_objects as go
import pandas as pd

from horloadist.zbeam import ZBeamElement
from horloadist.polygon import Polygon


ZBEAM_STYLE = {
    'line': {'color': 'black'},
}

F_INNER_STYLE = {
    'line': {'color': 'orange'},
}



def init_go():
    fig = go.Figure()
    return fig



def to_go_beam(
        fig:go.Figure,
        zbeam:ZBeamElement
        ) -> go.Figure:
    
    fig.add_trace(
        go.Scatter3d(
            x=zbeam._glo_x_cords,
            y=zbeam._glo_y_cords,
            z=zbeam._glo_z_cords,
            mode='lines',
            name=f'beam nr {zbeam._no}',
            **ZBEAM_STYLE
        )
    )

    return fig


def to_go_x_shear(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    x_vals = zbeam._glo_x_cords + zbeam._glo_x_shear * scale

    customdata = zbeam._result_table.values

    hovertemplate = (
        '<br>Vx: %{customdata[4]:.2f}'
        '<br>X %{customdata[1]:.2f}'
        '<br>Y %{customdata[2]:.2f}'
        '<br>Z %{customdata[3]:.2f}'
        )

    fig.add_trace(
        go.Scatter3d(
            x=x_vals,
            y=zbeam._glo_y_cords,
            z=zbeam._glo_z_cords,
            mode='lines',
            name=f'glo Vx {zbeam._no}',
            customdata=customdata,
            hovertemplate=hovertemplate,
            **F_INNER_STYLE
        )
    )

    return fig

def to_go_y_shear(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    y_vals = zbeam._glo_y_cords + zbeam._glo_y_shear * scale

    customdata = zbeam._result_table.values

    hovertemplate = (
        '<br>Vy: %{customdata[5]:.2f}'
        '<br>X %{customdata[1]:.2f}'
        '<br>Y %{customdata[2]:.2f}'
        '<br>Z %{customdata[3]:.2f}'
        )

    fig.add_trace(
        go.Scatter3d(
            x=zbeam._glo_x_cords,
            y=y_vals,
            z=zbeam._glo_z_cords,
            mode='lines',
            name=f'glo Vy {zbeam._no}',
            customdata=customdata,
            hovertemplate=hovertemplate,
            **F_INNER_STYLE
        )
    )

    return fig


def to_go_z_normf(
        fig:go.Figure,
        zbeam:ZBeamElement,
        scale:float=1
        ) -> go.Figure:
    
    x_vals = zbeam._glo_x_cords + zbeam._glo_z_normf * scale

    customdata = zbeam._result_table.values

    hovertemplate = (
        '<br>N: %{customdata[8]:.2f}'
        '<br>X %{customdata[1]:.2f}'
        '<br>Y %{customdata[2]:.2f}'
        '<br>Z %{customdata[3]:.2f}'
        )

    fig.add_trace(
        go.Scatter3d(
            x=x_vals,
            y=zbeam._glo_y_cords,
            z=zbeam._glo_z_cords,
            mode='lines',
            name=f'N {zbeam._no}',
            customdata=customdata,
            hovertemplate=hovertemplate,
            **F_INNER_STYLE
        )
    )

    return fig