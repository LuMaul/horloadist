# Calculate Load Distribution In The Plane

> Caution! Do not blindly trust this calculation, but always check the plausibility of the results.

This project provides a tool for structural analysis using the `horloadist` library. You can define a 2D polygon in the x-y plane representing a plate, along with supports that represent walls and their bending stiffnesses around the x and y axes. Currently, it only works with constant stiffness values.

## Example Output

```
polyg. area           : 375.0000
polyg. centre [xm,ym] : 0.0000, 0.0000
stiff. centre [xs,ys] : 2.5000, 4.7727
EIx total             : 9.4
EIy total             : 34.4
EIw total             : 1,931.8

   node nr     x    y  x-xm  y-ym  xm-xs       ym-ys     EIy    EIx     % EIx     % EIy    % EIwx    % EIwy
0        1 -10.0 -2.5 -10.0  -2.5    12.5   7.272727   3.125  0.000  0.090909  0.000000  0.011765  0.000000
1        2 -12.5  0.0 -12.5   0.0    15.0   4.772727   0.000  3.125  0.000000  0.333333  0.000000  0.024265
2        3 -10.0  2.5 -10.0   2.5    12.5   2.272727   3.125  0.000  0.090909  0.000000  0.003676  0.000000
3        4   0.0 -7.5   0.0  -7.5     2.5  12.272727   3.125  0.000  0.090909  0.000000  0.019853  0.000000
4        5   2.5  7.5   2.5   7.5     0.0  -2.727273  25.000  0.000  0.727273  0.000000 -0.035294  0.000000
5        6   7.5  0.0   7.5   0.0    -5.0   4.772727   0.000  3.125  0.000000  0.333333  0.000000 -0.008088
6        7  12.5 -5.0  12.5  -5.0   -10.0   9.772727   0.000  3.125  0.000000  0.333333  0.000000 -0.016176

Fx, Fy    : 0, 1
tor. Ts,x : -0.0000
tor. Ts,y : -2.5000
tor. Ts   : -2.5000

   node nr  Vx ~ EIx  Vy ~ EIy  Vx ~ EIwx  Vy ~ EIwy        Vx        Vy
0        1       0.0  0.000000  -0.029412  -0.000000  0.029412  0.000000
1        2       0.0  0.333333  -0.000000  -0.060662  0.000000  0.272672
2        3       0.0  0.000000  -0.009191  -0.000000  0.009191  0.000000
3        4       0.0  0.000000  -0.049632  -0.000000  0.049632  0.000000
4        5       0.0  0.000000   0.088235  -0.000000 -0.088235  0.000000
5        6       0.0  0.333333  -0.000000   0.020221  0.000000  0.353554
6        7       0.0  0.333333  -0.000000   0.040441  0.000000  0.373775
```


## Prerequisites

- Python 3.x
- `horloadist` library

## Installation

Clone this repository:
```
git clone https://github.com/LuMaul/hor_load_dist.git
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
w1 = SupportNode(1, -10.0, -2.5, globalIx(5, 0.3), globalIy(5, 0.3))
# ... (other nodes)

# Define the plate
plate = Polygon([[-12.5, -7.5], [-12.5, 7.5], [12.5, 7.5], [12.5, -7.5]])

# Create and solve the structure
struc = Stucture(plate, [w1, w2, w3, w4, w5, w6, w7])
sol = LinSolve(struc, 0, 1)

# Print results
struc.printTable()
sol.printTable()
```

## Caution




## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
