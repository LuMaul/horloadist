# from RFEM.initModel import Model, Calculate_all
from RFEM.BasicObjects.material import Material
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.line import Line
from RFEM.BasicObjects.surface import Surface
from RFEM.BasicObjects.thickness import Thickness
from RFEM.TypesForNodes.nodalSupport import NodalSupport
from RFEM.LoadCasesAndCombinations.loadCase import LoadCase
from RFEM.Loads.freeLoad import FreeLoad
from RFEM.dataTypes import inf
from RFEM.enums import (
    MaterialModel,
    MaterialType,
    MaterialDefinitionType,
    FreeConcentratedLoadLoadDirection,
    FreeLoadLoadProjection
    )

import os
import __main__

from horloadist.node import SupportNode
from horloadist.polygon import Polygon
from horloadist.loads import XYLoad

# finish this on windows

def init_rfem_model(**kwargs) -> None:
    kwargs.setdefault('model_name', f'{os.path.basename(__main__.__file__)}.rf6')
    # Model(**args)



def to_rfem_support_node(node:SupportNode) -> dict:
    # Node(
    #     no=node._nr,
    #     coordinate_X=node._glob_x,
    #     coordinate_Y=node._glob_y,
    # )
    # NodalSupport.Nonlinearity(
    #     no=node._nr,
    #     nodes=f'{node._nr}',
    #     spring_constant=[
    #         node._glob_EIy,
    #         node._glob_EIx,
    #         inf,
    #         0.0,
    #         0.0,
    #         inf
    #         ]
    # )
    return {node._nr:[node._glo_x, node._glo_y]}


def to_rfem_nodes(polygon:Polygon) -> dict:
    OFFSET = 100 # To Do: automate available node nr recognition

    polygon_node_nrs_xy = dict(enumerate(polygon._xy, start=OFFSET))

    for node_nr, (x, y) in polygon_node_nrs_xy.items():
        # Node(no=node_nr, coordinate_X=x, coordinate_Y=y)
        pass

    return polygon_node_nrs_xy


def to_rfem_lines(polygon:Polygon) -> dict:
    OFFSET = 100 # To Do: automate available node nr recognition

    node_nrs = list(to_rfem_nodes(polygon))
    start_end_node_nrs = list(zip(node_nrs, node_nrs[1:] + node_nrs[:1]))
    line_nrs_sta_end_node_nrs = dict(enumerate(start_end_node_nrs, start=OFFSET))

    for line_nr, (start_nr, end_nr) in line_nrs_sta_end_node_nrs.items():
        # Line(no=line_nr, nodes_no=f'{start_nr} {end_nr}')
        pass

    return line_nrs_sta_end_node_nrs


def to_rfem_shell(polygon:Polygon) -> dict:
    SHELL_MAT_TAG = 1 # To Do: automate available node nr recognition

    # Material.UserDefinedMaterial(
    #     no= SHELL_MAT_TAG,
    #     name= 'EA GAv -> oo',
    #     material_type = MaterialType.TYPE_BASIC,
    #     material_model = MaterialModel.MODEL_ISOTROPIC_LINEAR_ELASTIC,
    #     elasticity_modulus=10e14,
    #     shear_modulus= 10e14,
    #     poisson_ratio=-0.5,
    #     mass_density=25*10**2,
    #     definition_type=MaterialDefinitionType.E_G_NO_NU,
    # )

    line_nrs = ' '.join(map(str, to_rfem_lines(polygon)))

    SHELL_THICKNESS_TAG = 1 # To Do: automate available node nr recognition

    # Thickness(
    #     no=SHELL_THICKNESS_TAG,
    #     uniform_thickness_d=0.30,
    # )

    SHELL_TAG = 1 # To Do: automate available node nr recognition

    # Surface(
    #     no=SHELL_TAG,
    #     boundary_lines_no=line_nrs,
    #     thickness=SHELL_THICKNESS_TAG
    # )

    return {SHELL_TAG:line_nrs}




def to_rfem_free_load(glo_x:float, glo_y:float, surface:int, load:XYLoad) -> dict:

    LOADCASE_TAG = 1 # To Do: automate available node nr recognition

    # LoadCase(no=LOADCASE_TAG, name='const horizontal', self_weight=[False, 0, 0, 1])

    OFFSET_X = 1 # To Do: automate available node nr recognition
    OFFSET_Y = 2 # To Do: automate available node nr recognition

    fx, fy = load._x_magnitude, load._y_magnitude

    # FreeLoad.ConcentratedLoad(
    #     no=OFFSET_X,
    #     load_case_no=LOADCASE_TAG,
    #     surfaces_no=f'{surface}',
    #     load_direction=FreeConcentratedLoadLoadDirection.LOAD_DIRECTION_GLOBAL_X,
    #     load_projection=FreeLoadLoadProjection.LOAD_PROJECTION_XY_OR_UV,
    #     load_parameter=[fx, glo_x, glo_y]
    # )

    # FreeLoad.ConcentratedLoad(
    #     no=OFFSET_Y,
    #     load_case_no=LOADCASE_TAG,
    #     surfaces_no=f'{surface}',
    #     load_direction=FreeConcentratedLoadLoadDirection.LOAD_DIRECTION_GLOBAL_Y,
    #     load_projection=FreeLoadLoadProjection.LOAD_PROJECTION_XY_OR_UV,
    #     load_parameter=[fy, glo_x, glo_y]
    # )

