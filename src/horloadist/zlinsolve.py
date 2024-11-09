from horloadist.zbeam import ZBeamElement
from horloadist.node import XYSupportNode
from horloadist.linsolve import LinSolve



class ZLinSolve:
    """
    A class for performing pseudo-3D structural analysis based on linear solution results.

    This class extends 2D linear analysis results into 3D by creating pseudo Z-beam
    elements at support nodes.

    Parameters
    ----------
    linsolve : LinSolve
        Linear solution object containing 2D analysis results.
    z_num_floors : int, optional
        Number of floors in the Z direction, by default 5.
    z_floor_heigt : float, optional
        Height of each floor, by default 3.00.

    Attributes
    ----------
    _linsolve : LinSolve
        Reference to the linear solution object.
    _result_table : pd.DataFrame
        Results table from linear solution.
    _z_num_floors : int
        Number of floors.
    _z_floor_heigt : float
        Height of each floor.
    """
    def __init__(
            self,
            linsolve:LinSolve,
            z_num_floors:int=5,
            z_floor_heigt:float=3.00,
            ) -> None:

        self._linsolve = linsolve
        self._result_table = self._linsolve._result_table
        self._z_num_floors = z_num_floors
        self._z_floor_heigt = z_floor_heigt


    def _extract_glo_f_x(self, node:XYSupportNode) -> float:
        f_x = self._result_table['Vx'].loc[self._result_table['node nr'] == node._nr]
        return float(f_x.iloc[0])

    def _extract_glo_f_y(self, node:XYSupportNode) -> float:
        f_y = self._result_table['Vy'].loc[self._result_table['node nr'] == node._nr]
        return float(f_y.iloc[0])


    def _extract_glo_f_z(self, node:XYSupportNode) -> float:
        if 'RFEM Vz' in self._result_table:
            f_z = self._result_table['RFEM Vz'].loc[
                self._result_table['node nr'] == node._nr
                ]
            return float(f_z.iloc[0])
        else:
            return 0.0

    @property
    def pseudo_beams(self) -> list[ZBeamElement]:
        """
        Create pseudo Z-beam elements for all nodes in the structure.

        Returns
        -------
        list[ZBeamElement]
            List of ZBeamElement objects created for each node in the structure.
        """
        pseudo_beams = []
        for node in self._linsolve._structure._nodes:
            ps_beam = ZBeamElement(
                node=node,
                z_num_floors=self._z_num_floors,
                z_floor_heigt=self._z_floor_heigt,
                const_f_x=self._extract_glo_f_x(node),
                const_f_y=self._extract_glo_f_y(node),
                const_f_z=self._extract_glo_f_z(node),
            )
            pseudo_beams.append(ps_beam)
        return pseudo_beams





if __name__ == '__main__':
    import pickle

    with open('test_linsolve.pkl', 'rb') as file:
        sol:LinSolve = pickle.load(file)

    beams = ZLinSolve(linsolve=sol, z_num_floors=5, z_floor_heigt=3.00).pseudo_beams

    for beam in beams:
        beam.printTable()
        print('\n')


