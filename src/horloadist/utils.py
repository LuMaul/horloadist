from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as mpl_axes
import matplotlib.figure as mpl_fig
from datetime import datetime


def interpolateXY(df:pd.DataFrame, Momentum:float|int) -> float:
    
    x_val = df['mom']
    y_val = df['EI']

    interpolation_function = interp1d(
        x_val,
        y_val,
        kind='linear',
        fill_value="extrapolate"
        )

    stiffness:np.ndarray = interpolation_function(Momentum)

    return float(stiffness)



def plot_nlsolve(
        res_table:pd.DataFrame,
        show:bool=True,
        save:bool=False,
        format:str='.pdf'
        ) -> None:

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    fig:mpl_fig.Figure = fig

    fig.tight_layout(pad=3)

    fig.suptitle('non linear iteration progress', fontsize=13)

    def plot_cols(
            ax:mpl_axes.Axes,
            cols:list,
            ylab:str
            ) -> None:

        for col in cols:
            ax.plot(res_table.index, res_table[col], label=col)
            ax.set_xlabel('iteration nr')
            ax.set_ylabel(ylab)
            ax.legend(frameon=False)


    def plot_xy_s(ax: mpl_axes.Axes, xCol: str, yCol: str) -> None:
        x = res_table[xCol]
        y = res_table[yCol]

        ax.plot(x, y, label='path of stiffness center', color='gray', zorder=1)

        ax.scatter(x.iloc[0], y.iloc[0], color='red', label='First point', zorder=2)
        ax.scatter(x.iloc[-1], y.iloc[-1], color='blue', label='Last point', zorder=2)

        ax.annotate(f'{res_table.index[0]}', (x.iloc[0], y.iloc[0]),
                    textcoords="offset points", xytext=(5, 5), ha='center', zorder=3)
        ax.annotate(f'{res_table.index[-1]}', (x.iloc[-1], y.iloc[-1]),
                    textcoords="offset points", xytext=(5, 5), ha='center', zorder=3)

        ax.set_xlabel('global $x$')
        ax.set_ylabel('global $y$')
        ax.legend(frameon=False)


    v_cols = [col for col in res_table.columns if 'V' in col]
    m_cols = [col for col in res_table.columns if 'M' in col]
    k_cols = [col for col in res_table.columns if 'EI' in col]

    plot_cols(axes[0, 0], v_cols, 'shear forces  $V$')
    plot_cols(axes[0, 1], m_cols, 'moments  $M$')
    plot_cols(axes[1, 0], k_cols, 'bending stiffness  $EI$')
    plot_xy_s(axes[1, 1], 'x_s', 'y_s')

    if save:
        current_time = datetime.now()
        formatted_time = f'{current_time:%Y-%m-%d_%H%M%S}'
        plt.savefig(f'{formatted_time}_nlsolve{format}')

    if show:
        plt.show()