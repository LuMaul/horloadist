
from horloadist.node import XYSupportNode
from horloadist.linsolve import LinSolve

class _PseudoBeam:
    def __init__(
            self,
            no:int,
            z_heigt:float,
            z_division:float,
            const_f_x:float,
            const_f_y:float,
            const_f_z:float,
            ) -> None:
        
        print(no, z_heigt, z_division, const_f_x, const_f_y, const_f_z)


class Pseudo3DSolve:
    def __init__(
            self,
            linsolve:LinSolve,
            z_number:int=5,
            z_division:float=3.00,
            ) -> None:
        
        self._linsolve = linsolve
        self._result_table = self._linsolve._result_table
        self._z_number = z_number
        self._z_division = z_division

        self._main()

    @property
    def _z_heigt(self) -> float:
        return self._z_division * self._z_number


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
    def _pseudo_beams(self) -> list[_PseudoBeam]:
        pseudo_beams = []
        for node in self._linsolve._structure._nodes:
            ps_beam = _PseudoBeam(
                no=node._nr,
                z_heigt=self._z_heigt,
                z_division=self._z_division,
                const_f_x=self._extract_glo_f_x(node),
                const_f_y=self._extract_glo_f_y(node),
                const_f_z=self._extract_glo_f_z(node),
            )
            pseudo_beams.append(ps_beam)
        return pseudo_beams
            
            
    def _main(self) -> None:
        self._pseudo_beams
    






if __name__ == '__main__':
    import pickle

    with open('test_linsolve.pkl', 'rb') as file:
        sol:LinSolve = pickle.load(file)

    Pseudo3DSolve(linsolve=sol)