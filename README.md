# `horloadist`

Calculate **hor**izontal **load** **dist**ribution on multiple supports of a single shell assuming $EA \to \infty$ .

> Caution! Do not blindly trust this calculation, but always check the plausibility of the results.

This project provides a tool for structural analysis using the `horloadist` library. You can define a 2D polygon in the x-y plane representing a shell, along with supports that represent walls and their bending stiffnesses around the x and y axes. Afterwards you can calculate the horizontal reaction forces on the support nodes (walls). Use `NonLinSolve` for solving systems iteratively with nonlinear wall bending stiffnesses taken from user created csv files.

## Example Table Output of `LinSolve`

```
polyg. area           : 375.0000
polyg. centre [xm,ym] : 0.0000, 0.0000 
stiff. centre [xs,ys] : 2.4672, -4.7664
EIx total             : 9.4
EIy total             : 34.4
EIw total             : 1,937.0

   node nr     x    y  x-xm  y-ym     xm-xs       ym-ys      EIx       EIy     % EIx     % EIy    % EIwx        % EIwy
0        1 -10.0  2.5 -10.0   2.5  12.467197  -7.266411  0.01125   3.12500  0.090820  0.001193 -0.011723 -7.240963e-05
1        2 -12.5  0.0 -12.5   0.0  14.967197  -4.766411  3.12500   0.01125  0.000327  0.331345 -0.000028 -2.414713e-02
2        3 -10.0 -2.5 -10.0  -2.5  12.467197  -2.266411  0.01125   3.12500  0.090820  0.001193 -0.003656 -7.240963e-05
3        4   0.0  7.5   0.0   7.5   2.467197 -12.266411  0.01125   3.12500  0.090820  0.001193 -0.019790 -1.432951e-05
4        5   2.5 -7.5   2.5  -7.5  -0.032803   2.733589  0.02250  25.00000  0.726559  0.002386  0.035282  3.810425e-07
5        6   7.5  0.0   7.5   0.0  -5.032803  -4.766411  3.12500   0.01125  0.000327  0.331345 -0.000028  8.119605e-03
6        7  12.5  5.0  12.5   5.0 -10.032803  -9.766411  3.12500   0.01125  0.000327  0.331345 -0.000057  1.618629e-02


Fx, Fy    : 0, -1
tor. Ts,x : 0.0000
tor. Ts,y : 2.4672
tor. Ts   : 2.4672

   node nr  Vx ~ EIx  Vy ~ EIy  Vx ~ EIwx     Vy ~ EIwy        Vx        Vy
0        1       0.0 -0.001193   0.028923 -1.786488e-04 -0.028923 -0.001371
1        2       0.0 -0.331345   0.000068 -5.957571e-02 -0.000068 -0.390921
2        3       0.0 -0.001193   0.009021 -1.786488e-04 -0.009021 -0.001371
3        4       0.0 -0.001193   0.048825 -3.535372e-05 -0.048825 -0.001228
4        5       0.0 -0.002386  -0.087047  9.401069e-07  0.087047 -0.002385
5        6       0.0 -0.331345   0.000068  2.003266e-02 -0.000068 -0.311313
6        7       0.0 -0.331345   0.000140  3.993476e-02 -0.000140 -0.291411
```

## Example Output of `NonLinSolve`

Output of `plot_nlsolve` from `NONLIN_main.py` in the examples directory:

![non linear example](example_nlsolve.png "non linear convergation process")


## Prerequisites

- `horloadist` library
- Python 3.x
- pandas
- numpy
- matplotlib
- datetime

## Installation

install via pip:
```
pip install horloadist
```


## Usage

The main script demonstrates how to use the `horloadist` library to create a structural model and solve it. Here's a brief overview of the process:

1. Import necessary classes from `horloadist`:
   ```python
   from horloadist import SupportNode, Polygon, Stucture, LinSolve
   ```

2. Define helper functions for moment of inertia calculations:
   ```python
   def globalIy(dx, dy):
       # ...
    
   def globalIx(dx, dy):
       # ...
   ```

3. Create support nodes using the `SupportNode` class.
4. Define the structure's shape using the `Polygon` class.
5. Create a `Stucture` object with the defined polygon and support nodes.
6. Solve the structure using `LinSolve`.
7. Print the results.

## Example

The provided example creates a plate structure with seven support nodes and solves it for a specific load case.

```python
# Create support nodes
w1 = SupportNode(1, -10.0,  2.5, globalIy(5, 0.3), globalIx(5, 0.3))
# ... (other nodes)

# Define the plate
plate = Polygon([[-12.5,-7.5], [12.5, -7.5], [12.5, 7.5], [-12.5, 7.5]])

# Create and solve the structure
struc = Stucture(plate, [w1, w2, w3, w4, w5, w6, w7])
sol = LinSolve(struc, 0, 1)

# Print results
struc.printTable()
sol.printTable()
```


## Possible Further Improvements

- add plot for geometry and force-vectors
- add plot for bending stiffnesses imported from csv files
- add angle param for `KX.globalRectangular(... , angle_from_x : float = ...)`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 