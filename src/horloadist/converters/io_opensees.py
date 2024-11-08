# not implemented yet
import o3seespy as o3

from horloadist.node import XYSupportNode
from horloadist.loads import Load

def init_ops_model(**model_kwargs) ->  o3.OpenSeesInstance:
    model_kwargs.setdefault('ndm', 2)
    model = o3.OpenSeesInstance(**model_kwargs)
    return model


def to_ops_node(model:o3.OpenSeesInstance, x:float, y:float) -> o3.node.Node:
    node = o3.node.Node(osi=model, x=x, y=y)
    return node


def to_ops_support(
        model:o3.OpenSeesInstance,
        node:XYSupportNode,
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
        e_mod=0,
    ) # not sure, if it's nescessary

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
        mats=[x_mat, y_mat],
        dirs=[o3.cc.DOF_X, o3.cc.DOF_Y]
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
        area=1.0,
        e_mod=10e14,
        iz=10e14,
        transf=transf
    )

    return beam


def to_ops_spider(
        model:o3.OpenSeesInstance,
        support_nodes:list[XYSupportNode],
        mass_centre_x:float,
        mass_centre_y:float
        ) -> o3.node.Node:
    
    mass_center = to_ops_node(model=model, x=mass_centre_x, y=mass_centre_y)
    
    for node in support_nodes:
        enode = to_ops_support(model=model, node=node)
        to_ops_rigid_beam(model=model, snode=mass_center, enode=enode)
    
    return model, mass_center
    
    
def to_ops_load(
        model:o3.OpenSeesInstance,
        mass_center:o3.node.Node,
        load:Load
        ) -> None:

    timesrs = o3.time_series.Constant(model)
    pattern = o3.pattern.Plain(model, timesrs)
    
    o3.Load(
        osi=model,
        node=mass_center,
        load_values=[load._x_magnitude, load._y_magnitude, 0]
    )

    constrs = o3.constraints.Plain(model)
    numbers = o3.numberer.RCM(model)
    system = o3.system.BandSPD(model)
    test = o3.test.NormDispIncr(model, tol=1.0e-10, max_iter=100_000)
    algo = o3.algorithm.ModifiedNewton(model)
    integr = o3.integrator.LoadControl(model, incr=0.1)
    analysis = o3.analysis.Static(model)
    analyze = o3.analyze(model)


if __name__ == '__main__':
    mod = init_ops_model()

    snode1 = XYSupportNode(nr=0, glo_x=0.00, glo_y=0.00, glo_kx=1.0, glo_ky=1.0)
    snode2 = XYSupportNode(nr=0, glo_x=5.00, glo_y=0.00, glo_kx=1.0, glo_ky=1.0)

    load = Load(0.00, -1000.0)

    mass_center_node = to_ops_node(mod, x=2.50, y=0.00)


    stiff_node1 = to_ops_support(mod, node=snode1)
    stiff_node2 = to_ops_support(mod, node=snode2)

    beam1 = to_ops_rigid_beam(mod, stiff_node1, mass_center_node)
    beam2 = to_ops_rigid_beam(mod, stiff_node2, mass_center_node)

    to_ops_load(mod, mass_center_node, load)

    forces1 = o3.get_ele_response(mod, beam1, 'force')
    forces2 = o3.get_ele_response(mod, beam2, 'force')
    disp = o3.get_node_disp(mod, node=stiff_node1)

    print(forces1)
    print(forces2)
    print(disp)

