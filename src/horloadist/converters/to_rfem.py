from RFEM.initModel import Model, Calculate_all
from RFEM.BasicObjects.node import Node
from RFEM.TypesForNodes.nodalSupport import NodalSupport
from RFEM.dataTypes import inf

from horloadist.node import SupportNode

def init_rfem_model(model_name:str, *args) -> None:
    Model(
        model_name=model_name,
        *args
    )
    Model.clientModel.service.begin_modification()


def to_rfem_node(node:SupportNode) -> None:
    Node(
        no=node._nr,
        coordinate_X=node._glob_x,
        coordinate_Y=node._glob_y,
    )
    NodalSupport.Nonlinearity(
        no=node._nr,
        nodes=f'{node._nr}',
        spring_constant=[
            node._glob_EIy,
            node._glob_EIy,
            inf,
            0.0,
            0.0,
            inf
            ]
    )