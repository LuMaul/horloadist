import pandas as pd
import numpy as np
import os
import __main__

from RFEM.initModel import Model, Calculate_all
from RFEM.BasicObjects.material import Material
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.line import Line
from RFEM.BasicObjects.surface import Surface
from RFEM.BasicObjects.thickness import Thickness
from RFEM.BasicObjects.opening import Opening
from RFEM.TypesForNodes.nodalSupport import NodalSupport
from RFEM.LoadCasesAndCombinations.loadCase import LoadCase
from RFEM.Loads.freeLoad import FreeLoad
from RFEM.Loads.surfaceLoad import SurfaceLoad
from RFEM.dataTypes import inf
from RFEM.Results.resultTables import ResultTables
from RFEM.Tools.GetObjectNumbersByType import GetAllObjects, GetObjectNumbersByType
from RFEM.enums import (
    ObjectTypes,
    MaterialModel,
    MaterialType,
    MaterialDefinitionType,
    FreeConcentratedLoadLoadDirection,
    FreeLoadLoadProjection
    )


from horloadist.node import XYSupportNode, ZSupportNode
from horloadist.polygon import Polygon
from horloadist.loads import Load


def _get_max_obj_nr(obj_type:ObjectTypes) -> int:
    nrs = GetObjectNumbersByType(obj_type)
    nrs_arr = np.array(nrs).flatten()
    if not nrs_arr.size == 0:
        return int(max(nrs_arr)) + 1
    return 1


def init_rfem_model(**kwargs) -> None:
    fname = os.path.basename(os.path.basename(__main__.__file__))
    kwargs.setdefault('model_name', f'{fname}')
    Model(**kwargs)



def to_rfem_xyzsupport_node(node:XYSupportNode) -> dict:
    Node(
        no=node._nr,
        coordinate_X=node._glo_x,
        coordinate_Y=node._glo_y,
        comment=f'{node._nr}'
    )
    kx, ky = node._glo_EIy*10e8, node._glo_EIx*10e8
    NodalSupport.Nonlinearity(
        no=node._nr,
        nodes=f'{node._nr}',
        spring_constant=[
            kx,
            ky,
            inf,
            0.0,
            0.0,
            0.0
            ],
        name=f'node nr {node._nr} {node._glo_EIy:0.4f} {node._glo_EIx:0.4f}'
    )
    return {node._nr:[node._glo_x, node._glo_y]}


def to_rfem_zsupport_node(node:ZSupportNode) -> dict:
    Node(
        no=node._nr,
        coordinate_X=node._glo_x,
        coordinate_Y=node._glo_y,
        comment=f'{node._nr}'
    )
    NodalSupport.Nonlinearity(
        no=node._nr,
        nodes=f'{node._nr}',
        spring_constant=[
            0.0,
            0.0,
            inf,
            0.0,
            0.0,
            0.0
            ],
        name=f'node nr {node._nr} vertical'
    )
    return {node._nr:[node._glo_x, node._glo_y]}


def to_rfem_nodes(polygon:Polygon) -> dict:

    node_no_start = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_NODE)

    polygon_node_nrs_xy = dict(enumerate(polygon._xy, start=node_no_start))

    for node_nr, (x, y) in polygon_node_nrs_xy.items():
        Node(no=node_nr, coordinate_X=x, coordinate_Y=y)

    return polygon_node_nrs_xy


def to_rfem_lines(polygon:Polygon) -> dict:

    line_no_start = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_LINE)

    node_nrs = list(to_rfem_nodes(polygon))
    start_end_node_nrs = list(zip(node_nrs, node_nrs[1:] + node_nrs[:1]))
    line_nrs_sta_end_node_nrs = dict(enumerate(start_end_node_nrs, start=line_no_start))

    for line_nr, (start_nr, end_nr) in line_nrs_sta_end_node_nrs.items():
        Line(no=line_nr, nodes_no=f'{start_nr} {end_nr}')

    return line_nrs_sta_end_node_nrs


def to_rfem_shell(polygon:Polygon) -> int:

    mat_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_MATERIAL)

    Material.UserDefinedMaterial(
        no= mat_no,
        name= 'E, G -> oo',
        material_type = MaterialType.TYPE_BASIC,
        material_model = MaterialModel.MODEL_ISOTROPIC_LINEAR_ELASTIC,
        elasticity_modulus=10e12,
        shear_modulus= 10e12,
        poisson_ratio=-0.5,
        mass_density=25*10**2,
        definition_type=MaterialDefinitionType.E_G_NO_NU,
    )

    line_nrs = ' '.join(map(str, to_rfem_lines(polygon)))

    thickness_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_THICKNESS)

    Thickness(
        no=thickness_no,
        uniform_thickness_d=0.30,
        material_no=mat_no
    )

    shell_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_SURFACE)

    Surface(
        no=shell_no,
        boundary_lines_no=line_nrs,
        thickness=thickness_no
    )

    return shell_no


def to_rfem_opening(polygon:Polygon) -> None:
    
    opening_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_OPENING)

    line_nrs = ' '.join(map(str, to_rfem_lines(polygon)))
    
    Opening(no=opening_no, lines_no=line_nrs)


def to_rfem_free_load(
        glo_x:float,
        glo_y:float,
        surface:int,
        load:Load,
        z_load:float|None=None
        ) -> int:

    loadcase_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_LOAD_CASE)

    LoadCase(no=loadcase_no, name='io rfem loadcase', self_weight=[False])

    fx, fy = load._x_magnitude*10e2, load._y_magnitude*10e2

    if fx != 0:
        freeload_x_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_FREE_CONCENTRATED_LOAD)
        FreeLoad.ConcentratedLoad(
            no=freeload_x_no,
            load_case_no=loadcase_no,
            surfaces_no=f'{surface}',
            load_direction=FreeConcentratedLoadLoadDirection.LOAD_DIRECTION_GLOBAL_X,
            load_projection=FreeLoadLoadProjection.LOAD_PROJECTION_XY_OR_UV,
            load_parameter=[fx, glo_x, glo_y]
        )

    if fy != 0:
        freeload_y_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_FREE_CONCENTRATED_LOAD)
        FreeLoad.ConcentratedLoad(
            no=freeload_y_no,
            load_case_no=loadcase_no,
            surfaces_no=f'{surface}',
            load_direction=FreeConcentratedLoadLoadDirection.LOAD_DIRECTION_GLOBAL_Y,
            load_projection=FreeLoadLoadProjection.LOAD_PROJECTION_XY_OR_UV,
            load_parameter=[fy, glo_x, glo_y]
        )

    if z_load:
        z_load_no = _get_max_obj_nr(ObjectTypes.E_OBJECT_TYPE_SURFACE_LOAD)
        SurfaceLoad(
            no=z_load_no,
            load_case_no=loadcase_no,
            surface_no=f'{surface}',
            magnitude=z_load*10e2
        )

    return loadcase_no



def from_rfem_nodeXForce(node_nr:int, loadcase_no:int) -> tuple:
    rx = ResultTables.NodesSupportForces(loading_no=loadcase_no)[node_nr][
        'support_force_p_x'
        ]
    return rx/10e2

def from_rfem_nodeYForce(node_nr:int, loadcase_no:int) -> tuple:
    ry = ResultTables.NodesSupportForces(loading_no=loadcase_no)[node_nr][
        'support_force_p_y'
        ]
    return ry/10e2

def from_rfem_nodeZForce(node_nr:int, loadcase_no:int) -> tuple:
    ry = ResultTables.NodesSupportForces(loading_no=loadcase_no)[node_nr][
        'support_force_p_z'
        ]
    return ry/10e2



def from_rfem_XForces(node_nrs:list[int], loadcase_no:int) -> pd.Series:
    return pd.Series([from_rfem_nodeXForce(node_nr-1, loadcase_no) for node_nr in node_nrs])

def from_rfem_YForces(node_nrs:list[int], loadcase_no:int) -> pd.Series:
    return pd.Series([from_rfem_nodeYForce(node_nr-1, loadcase_no) for node_nr in node_nrs])

def from_rfem_ZForces(node_nrs:list[int], loadcase_no:int) -> pd.Series:
    return pd.Series([from_rfem_nodeZForce(node_nr-1, loadcase_no) for node_nr in node_nrs])



