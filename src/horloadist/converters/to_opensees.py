# not implemented yet
import o3seespy as o3

from horloadist.node import SupportNode
from horloadist.loads import XYLoad

def init_ops_model(**model_kwargs) ->  o3.OpenSeesInstance:
    model_kwargs.setdefault('ndm', 2)
    model = o3.OpenSeesInstance(**model_kwargs)
    return model


def to_ops_node(model:o3.OpenSeesInstance, x:float, y:float) -> o3.node.Node:
    node = o3.node.Node(osi=model, x=x, y=y)
    return node


def to_ops_support(
        model:o3.OpenSeesInstance,
        node:SupportNode,
        ) -> o3.node.Node:
    
    fixed_node = to_ops_node(model=model, x=node._glo_x, y=node._glo_y)
    stiff_node = to_ops_node(model=model, x=node._glo_x, y=node._glo_y)

    x_mat = o3.uniaxial_material.Elastic(
        osi=model,
        e_mod=node._glo_EIy
    )

    y_mat = o3.uniaxial_material.Elastic(
        osi=model,
        e_mod=node._glo_EIx
    )

    z_mat = o3.uniaxial_material.Elastic(
        osi=model,
        e_mod=10e-10,
    )

    o3.Fix3DOF(
        osi=model,
        node=fixed_node,
        x=o3.cc.FIXED,
        y=o3.cc.FIXED,
        z_rot=o3.cc.FIXED
    )

    o3.element.zero_length.ZeroLength(
        osi=model,
        ele_nodes=[stiff_node, fixed_node],
        mats=[x_mat, y_mat, z_mat]
    )

    return stiff_node


def to_ops_rigid_beam(
        model:o3.OpenSeesInstance,
        snode:o3.node.Node,
        enode:o3.node.Node
        ) -> o3.element.ElasticBeamColumn2D:
    
    transf = o3.geom_transf.Linear2D(osi=model)
    
    beam = o3.element.ElasticBeamColumn2D(
        osi=model,
        ele_nodes=[snode, enode],
        area=10,
        e_mod=10e14,
        iz=10e14,
        transf=transf
    )

    return beam


def to_ops_spider(
        model:o3.OpenSeesInstance,
        support_nodes:list[SupportNode],
        mass_centre_x:float,
        mass_centre_y:float
        ) -> o3.node.Node:
    
    mass_center = to_ops_node(model=model, x=mass_centre_x, y=mass_centre_y)
    
    for node in support_nodes:
        enode = to_ops_support(model=model, node=node)
        to_ops_rigid_beam(model=model, snode=mass_center, enode=enode)
    
    return mass_center
    
    
def to_ops_load(
        model:o3.OpenSeesInstance,
        mass_center:o3.node.Node,
        load:XYLoad
        ) -> None:

    timesrs = o3.time_series.Constant(model)
    pattern = o3.pattern.Plain(model, timesrs)
    
    o3.Load(
        osi=model,
        node=mass_center,
        load_values=[load._x_magnitude, load._y_magnitude]
    )

    constrs = o3.constraints.Plain(model)
    numbers = o3.numberer.RCM(model)
    system = o3.system.BandSPD(model)
    test = o3.test.NormDispIncr(model, tol=1.0e-12, max_iter=10000)
    algo = o3.algorithm.ModifiedNewton(model)
    integr = o3.integrator.LoadControl(model, incr=0.1)
    analysis = o3.analysis.Static(model)
    analyze = o3.analyze(model)